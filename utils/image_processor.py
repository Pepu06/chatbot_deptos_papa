"""
Image processor
Download images from WhatsApp and upload to Supabase storage
"""
from services.whatsapp import whatsapp_service
from services.supabase_client import supabase_service
from typing import Optional
import hashlib
from datetime import datetime


async def process_whatsapp_image(
    media_id: str,
    user_id: str,
    bucket_name: str = "whatsapp-images"
) -> Optional[str]:
    """
    Download image from WhatsApp and upload to Supabase storage
    
    Args:
        media_id: WhatsApp media ID
        user_id: User ID for file naming
        bucket_name: Supabase storage bucket name
        
    Returns:
        Public URL of uploaded image or None if failed
    """
    try:
        # Download image from WhatsApp
        print(f"📥 Downloading image {media_id}...")
        image_data = await whatsapp_service.download_media(media_id)
        
        if not image_data:
            print("❌ Failed to download image")
            return None
        
        # Generate unique filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        file_hash = hashlib.md5(image_data).hexdigest()[:8]
        filename = f"{user_id}/{timestamp}_{file_hash}.jpg"
        
        # Upload to Supabase storage
        print(f"📤 Uploading image to Supabase: {filename}")
        public_url = await supabase_service.upload_image(
            bucket=bucket_name,
            file_path=filename,
            file_data=image_data
        )
        
        if public_url:
            print(f"✅ Image uploaded successfully: {public_url}")
            return public_url
        else:
            print("❌ Failed to upload image to Supabase")
            return None
            
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None
