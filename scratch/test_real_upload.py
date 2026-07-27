import sys
import os

# Add CWD to import path
sys.path.append(os.getcwd())

from app.supabase import upload_to_storage
from app.config import settings

def test_upload():
    print("--- Supabase Diagnostics ---")
    print(f"Supabase Project URL: {settings.SUPABASE_URL}")
    print(f"Target Storage Bucket: {settings.SUPABASE_STORAGE_BUCKET}")
    
    # Create tiny dummy PNG bytes
    dummy_png_bytes = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    file_path = "test/diagnostic_poster.png"
    
    try:
        print("\nAttempting upload to storage bucket...")
        public_url = upload_to_storage(
            bucket_name=settings.SUPABASE_STORAGE_BUCKET,
            file_path=file_path,
            file_bytes=dummy_png_bytes,
            content_type="image/png"
        )
        print("\n[SUCCESS] Upload finished successfully!")
        print(f"Public URL: {public_url}")
    except Exception as e:
        print("\n[FAILED] Upload failed with error:")
        print(f"Type: {type(e)}")
        print(f"Message: {str(e)}")

if __name__ == "__main__":
    test_upload()
