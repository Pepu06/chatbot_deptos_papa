"""
WhatsApp Business API client
Handles sending messages and downloading media
"""
import httpx
from config.settings import settings
from typing import Optional, Dict, Any
import asyncio


class WhatsAppService:
    """Service for interacting with WhatsApp Business API"""
    
    def __init__(self):
        self.base_url = settings.whatsapp_api_url
        self.token = settings.whatsapp_token
        self.phone_number_id = settings.whatsapp_phone_number_id or settings.whatsapp_client_id
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
    
    async def send_message(self, to: str, message: str) -> bool:
        """Send a text message"""
        try:
            # TESTING: Siempre enviar al número de prueba
            test_number = "+541140962011"  # Número de prueba sin el +
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": test_number,  # Forzar número de prueba
                "type": "text",
                "text": {
                    "body": message
                }
            }
            
            print(f"📤 Enviando mensaje a {test_number}: {message[:50]}...")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                print(f"✅ Mensaje enviado exitosamente!")
                return True
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            if hasattr(e, 'response') and hasattr(e.response, 'text'):
                print(f"   Response: {e.response.text}")
            return False
    
    async def send_template(
        self,
        to: str,
        template_name: str,
        language_code: str = "es",
        components: list = None
    ) -> bool:
        """Send a template message"""
        try:
            # TESTING: Siempre enviar al número de prueba
            test_number = "541140962011"
            
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": test_number,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            
            # Add components if provided (for templates with parameters/buttons)
            if components:
                payload["template"]["components"] = components
            
            print(f"📋 Enviando template '{template_name}' a {test_number}...")
            print(f"   Payload: {payload}")
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                
                # Check for errors
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"❌ Error {response.status_code} enviando template")
                    print(f"   Detalles: {error_detail}")
                    return False
                
                print(f"✅ Template enviado exitosamente!")
                return True
        except Exception as e:
            print(f"❌ Error sending template: {e}")
            if hasattr(e, 'response'):
                try:
                    print(f"   Response text: {e.response.text}")
                except:
                    pass
            return False
    
    async def download_media(self, media_id: str) -> Optional[bytes]:
        """
        Download media file from WhatsApp
        Returns file bytes if successful
        """
        try:
            # Step 1: Get media URL
            url = f"{self.base_url}/{media_id}"
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers)
                response.raise_for_status()
                media_data = response.json()
                
                if "url" not in media_data:
                    print(f"No URL in media response: {media_data}")
                    return None
                
                media_url = media_data["url"]
                
                # Step 2: Download the actual file
                response = await client.get(media_url, headers=self.headers)
                response.raise_for_status()
                
                return response.content
        except Exception as e:
            print(f"Error downloading media: {e}")
            return None
    
    async def mark_as_read(self, message_id: str) -> bool:
        """Mark a message as read"""
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(url, json=payload, headers=self.headers)
                response.raise_for_status()
                return True
        except Exception as e:
            print(f"Error marking message as read: {e}")
            return False


# Global instance
whatsapp_service = WhatsAppService()
