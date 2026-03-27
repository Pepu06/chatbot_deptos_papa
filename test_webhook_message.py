"""
Script para probar el webhook enviando un mensaje de prueba
"""
import requests
import json

# URL del webhook local
WEBHOOK_URL = "http://localhost:8000/webhook"

# Payload de un mensaje de texto normal
text_message_payload = {
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
                    "from": "5491140962011",
                    "id": "wamid.test123",
                    "timestamp": "1774632746",
                    "type": "text",
                    "text": {
                        "body": "Formosa 380 todo ok"
                    }
                }]
            },
            "field": "messages"
        }]
    }]
}

print("🧪 Testing WhatsApp Webhook with Text Message")
print("=" * 70)
print(f"\n📤 Sending POST request to: {WEBHOOK_URL}")
print(f"📝 Message: 'Formosa 380 todo ok'")
print("\nPayload:")
print(json.dumps(text_message_payload, indent=2))
print("\n" + "=" * 70)

try:
    response = requests.post(
        WEBHOOK_URL,
        json=text_message_payload,
        headers={"Content-Type": "application/json"},
        timeout=10
    )
    
    print(f"\n✅ Response Status: {response.status_code}")
    print(f"📄 Response Body: {response.json()}")
    
    if response.status_code == 200:
        print("\n✅ Webhook processed successfully!")
        print("\n📋 Check the server logs for:")
        print("   - Message processing details")
        print("   - Property Agent activity")
        print("   - Template sending confirmation")
    else:
        print(f"\n❌ Webhook returned error: {response.status_code}")
        print(f"   Details: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("\n❌ ERROR: Could not connect to server")
    print("   Make sure the server is running on http://localhost:8000")
    print("   Run: python main.py")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
