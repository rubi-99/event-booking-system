import sys
import os
import httpx

# Add CWD to path so we can import from app
sys.path.append(os.getcwd())

from jose import jwt, JWTError
from app.config import settings

def debug_token(token: str):
    print("=== JWT Debugger ===")
    try:
        header = jwt.get_unverified_header(token)
        print(f"JWT Header: {header}")
        alg = header.get("alg")
        print(f"Algorithm: {alg}")
    except Exception as e:
        print(f"Error parsing header: {e}")
        return

    # Try decoding without signature validation first to inspect claims
    try:
        claims = jwt.get_unverified_claims(token)
        print(f"Claims (unverified): {claims}")
        print(f"Audience ('aud'): {claims.get('aud')}")
        print(f"Subject ('sub'/user_id): {claims.get('sub')}")
    except Exception as e:
        print(f"Error reading claims: {e}")
        
    # Now try full cryptographic verification based on algorithm
    try:
        if alg in ["ES256", "RS256"]:
            # Fetch public key set from Supabase JWKS endpoint
            jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
            print(f"\nFetching JWKS from: {jwks_url}")
            response = httpx.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
            
            payload = jwt.decode(
                token,
                jwks,
                algorithms=[alg],
                audience="authenticated"
            )
        else:
            # Symmetric HS256 verification using local secret
            import base64
            secret_display = settings.SUPABASE_JWT_SECRET[:5] + "..." if settings.SUPABASE_JWT_SECRET else "None"
            print(f"\nVerifying with symmetric HS256 secret: {secret_display}")
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
            
        print("\n[SUCCESS] Token verified successfully!")
        print(f"Verified Payload: {payload}")
    except JWTError as e:
        print(f"\n[FAILED] Verification failed: {e}")
    except Exception as e:
        print(f"\n[FAILED] Unexpected error during verification: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: uv run python scratch/debug_jwt.py <YOUR_JWT_TOKEN>")
        sys.exit(1)
    debug_token(sys.argv[1])
