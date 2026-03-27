"""
Script para probar el envío de mensajes por WhatsApp
"""
import asyncio
from services.whatsapp import whatsapp_service
from config.settings import settings

async def test_send():
    print(f"🔧 Testing WhatsApp send...")
    print(f"  Client ID: {settings.whatsapp_client_id}")
    print(f"  Token: {settings.whatsapp_token[:20]}...")
    print(f"  Phone ID: {settings.whatsapp_phone_number_id}")
    
    # Intentar enviar un mensaje de prueba
    # NOTA: Reemplaza este número con tu número de WhatsApp de prueba
    test_number = "5491234567890"  # Cambia este número
    
    result = await whatsapp_service.send_message(
        to=test_number,
        message="🤖 Test desde el bot - Si recibes esto, ¡funciona!"
    )
    
    print(f"  Resultado: {'✅ Enviado' if result else '❌ Error'}")

if __name__ == "__main__":
    asyncio.run(test_send())
