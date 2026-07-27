from typing import List, Dict, Any
from uuid import UUID
import httpx
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.enums.roles import UserRole

# 1. Use HTTPBearer to read the Bearer token header
security = HTTPBearer()

# In-memory cache for JWKS keys to prevent network calls on every API request (optimizes scaling)
JWKS_CACHE: Dict[str, Any] = {}

async def get_jwks() -> Dict[str, Any]:
    """
    Fetches the JSON Web Key Set (JWKS) from Supabase.
    Caches it in memory for high-performance requests.
    """
    global JWKS_CACHE
    if not JWKS_CACHE:
        jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(jwks_url)
                response.raise_for_status()
                JWKS_CACHE = response.json()
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to retrieve signing keys from auth provider: {str(e)}"
            )
    return JWKS_CACHE

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    FastAPI dependency that decodes the client JWT token locally
    and fetches their corresponding user profile from the database.
    """
    token = credentials.credentials
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # 1. Inspect token headers to determine signing algorithm (HS256 vs ES256/RS256)
        header = jwt.get_unverified_header(token)
        alg = header.get("alg")
        
        # 2. Decode the token based on the algorithm type
        if alg in ["ES256", "RS256"]:
            # Asymmetric key verification (modern Supabase default)
            jwks = await get_jwks()
            payload = jwt.decode(
                token,
                jwks,
                algorithms=[alg],
                audience="authenticated"
            )
        else:
            # Symmetric key verification using local secret (legacy Supabase default)
            import base64
            try:
                padded_secret = settings.SUPABASE_JWT_SECRET + "=" * (4 - len(settings.SUPABASE_JWT_SECRET) % 4)
                secret_key = base64.b64decode(padded_secret)
            except Exception:
                secret_key = settings.SUPABASE_JWT_SECRET

            payload = jwt.decode(
                token,
                secret_key,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
            
        user_id = UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # 3. Get local profile matching this UUID
    return await UserService.get_user_profile(db, user_id)

def require_role(allowed_roles: List[UserRole]):
    """
    Role-based Access Control (RBAC) dependency factory.
    Example usage: Depends(require_role([UserRole.ORGANIZER]))
    """
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return current_user
    return dependency
