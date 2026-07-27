from supabase import create_client, Client
from app.config import settings

# A single shared Supabase Client instance
# We load the URL and service role key from settings to bypass RLS for server-side actions
supabase_client: Client = create_client(
    supabase_url=settings.SUPABASE_URL,
    supabase_key=settings.SUPABASE_SERVICE_ROLE_KEY
)

def upload_to_storage(bucket_name: str, file_path: str, file_bytes: bytes, content_type: str) -> str:
    """
    Uploads raw file bytes to a Supabase Storage bucket and returns its public URL.
    Note: Supabase Python SDK storage methods execute synchronously.
    """
    bucket = supabase_client.storage.from_(bucket_name)
    
    # Upload the binary payload
    bucket.upload(
        path=file_path,
        file=file_bytes,
        file_options={"content-type": content_type}
    )
    
    # Retrieve and return the public URL
    return bucket.get_public_url(file_path)
