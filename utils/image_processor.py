"""
Image processor
Descarga imágenes de WhatsApp para enviar a Gemini.
El almacenamiento en la nube es opcional y no bloquea el flujo.
"""
from services.whatsapp import whatsapp_service
from typing import Optional


async def process_whatsapp_image(
    media_id: str,
    user_id: str,
    bucket_name: str = "fotos_departamentos"
) -> Optional[str]:
    """
    Descarga la imagen de WhatsApp.
    Devuelve None (sin storage externo configurado actualmente).
    Los bytes de la imagen se usan directamente en Gemini via handle_message.
    """
    try:
        print(f"📥 Downloading image {media_id} for Gemini processing...")
        image_data = await whatsapp_service.download_media(media_id)
        if not image_data:
            print("❌ Failed to download image")
        return None
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None
