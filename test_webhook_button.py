"""
Script para probar el botón "/Si, guardar"
"""
import requests
import json

# URL del webhook local
WEBHOOK_URL = "http://localhost:8000/webhook"

# Payload del botón (formato REAL según WhatsApp API)
button_payload = {
    "object": "whatsapp_business_account",
    "entry": [{
        "id": "123456789",
        "changes": [{
            "value": {
                "messaging_product": "whatsapp",
                "metadata": {
                    "display_phone_number": "15551361110",
                    "phone_number_id": "426074767259019"
                },
                "contacts": [{
                    "profile": {"name": "Pedro Test"},
                    "wa_id": "5491140962011"
                }],
                "messages": [{
                    "context": {
                        "from": "15551361110",
                        "id": "wamid.previous_message_id"
                    },
                    "from": "5491140962011",
                    "id": "wamid.button_response_id",
                    "timestamp": "1774632750",
                    "type": "button",
                    "button": {
                        "payload": "/Si, guardar.",
                        "text": "/Si, guardar."
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

print("🧪 Testing WhatsApp Button Response")
print("=" * 70)
print(f"\n📤 Sending POST request to: {WEBHOOK_URL}")
print(f"🔘 Button pressed: '/Si, guardar.'")
print("\nPayload:")
print(json.dumps(button_payload, indent=2))
print("\n" + "=" * 70)

try:
    response = requests.post(
        WEBHOOK_URL,
        json=button_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Button webhook processed successfully!")
        print("\n📋 Check the server logs for:")
        print("   - '📱 Button received: /Si, guardar.'")
        print("   - '📅 Using Calendar Agent'")
        print("   - Calendar event creation")
    else:
        print(f"\n❌ Webhook returned error: {response.status_code}")
        print(f"   Details: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to server")
    print("   Make sure the server is running on http://localhost:8000")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
