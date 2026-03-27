"""
Test para verificar el manejo de botones interactivos de WhatsApp
"""
import json
from models.message import WhatsAppWebhook

# Ejemplo de webhook que llega cuando el usuario presiona un botón
button_webhook_payload = {
    "object": "whatsapp_business_account",
    "entry": [
        {
            "id": "123456789",
            "changes": [
                {
                    "value": {
                        "messaging_product": "whatsapp",
                        "metadata": {
                            "display_phone_number": "15551234567",
                            "phone_number_id": "123456789"
                        },
                        "contacts": [
                            {
                                "profile": {
                                    "name": "Pedro"
                                },
                                "wa_id": "541140962011"
                            }
                        ],
                        "messages": [
                            {
                                "from": "541140962011",
                                "id": "wamid.123456",
                                "timestamp": "1234567890",
                                "type": "interactive",
                                "interactive": {
                                    "type": "button_reply",
                                    "button_reply": {
                                        "id": "button_si",
                                        "title": "/Si, guardar",
                                        "text": "/Si, guardar"
                                    }
                                }
                            }
                        ]
                    },
                    "field": "messages"
                }
            ]
        }
    ]
}

# Test de parseo
print("🧪 Testing WhatsApp Interactive Button Webhook...")
print("=" * 60)

try:
    webhook = WhatsAppWebhook(**button_webhook_payload)
    print("✅ Webhook parsed successfully!")
    print(f"   Object: {webhook.object}")
    print(f"   Entry count: {len(webhook.entry)}")
    
    for entry in webhook.entry:
        for change in entry.changes:
            if change.value.messages:
                for message in change.value.messages:
                    print(f"\n📱 Message Details:")
                    print(f"   Type: {message.type}")
                    print(f"   From: {message.from_}")
                    print(f"   Timestamp: {message.timestamp}")
                    
                    if message.interactive:
                        print(f"   Interactive Type: {message.interactive.type}")
                        if message.interactive.button_reply:
                            print(f"   Button Text: {message.interactive.button_reply.text}")
                            print(f"   Button Payload: {message.interactive.button_reply.payload}")
    
    print("\n✅ Test passed! Interactive buttons are now supported.")
    
except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()

print("=" * 60)
