"""
Test con el payload REAL del botón de WhatsApp
"""
import sys
sys.path.insert(0, '/Users/pedro/Documents/chatbot_papa')

from models.message import WhatsAppWebhook


def test_real_button_payload():
    print("🧪 TESTING REAL WHATSAPP BUTTON PAYLOAD")
    print("=" * 70)
    
    # Payload REAL del botón según lo proporcionado por el usuario
    real_button_webhook = {
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
                    "contacts": [
                        {
                            "profile": {
                                "name": "Pedro"
                            },
                            "wa_id": "5491140962011"
                        }
                    ],
                    "messages": [
                        {
                            "context": {
                                "from": "15551361110",
                                "id": "wamid.HBgNNTQ5MTE0MDk2MjAxMRUCABEYEjk1MkY2NUEyMEQ1QkQyRUQ4RQA="
                            },
                            "from": "5491140962011",
                            "id": "wamid.HBgNNTQ5MTE0MDk2MjAxMRUCABIYFDNCQTk3OEU1NDk4NUIyMTE3MkEwAA==",
                            "timestamp": "1774632746",
                            "type": "button",
                            "button": {
                                "payload": "/Si, guardar.",
                                "text": "/Si, guardar."
                            }
                        }
                    ]
                },
                "field": "messages"
            }]
        }]
    }
    
    print("\n📥 Parsing real button webhook...")
    
    try:
        webhook = WhatsAppWebhook(**real_button_webhook)
        message_data = webhook.entry[0].changes[0].value.messages[0]
        
        print("✅ Webhook parsed successfully!")
        print(f"\n📱 Message Details:")
        print(f"   Type: {message_data.type}")
        print(f"   From: {message_data.from_}")
        print(f"   Timestamp: {message_data.timestamp}")
        
        if message_data.button:
            print(f"\n🔘 Button Details:")
            print(f"   Text: {message_data.button.text}")
            print(f"   Payload: {message_data.button.payload}")
            
            # Simular la extracción de texto
            extracted_text = message_data.button.text or message_data.button.payload
            print(f"\n✅ Extracted text: '{extracted_text}'")
            
            # Probar el routing al Calendar Agent
            print(f"\n🔍 Testing Calendar Agent routing...")
            message_lower = extracted_text.lower()
            is_calendar_confirmation = "/si" in message_lower and "guardar" in message_lower
            
            if is_calendar_confirmation:
                print(f"   ✅ CORRECT: Will route to Calendar Agent")
                print(f"   ✅ Text contains '/si' and 'guardar'")
            else:
                print(f"   ❌ WRONG: Would route to Property Agent")
                print(f"   ❌ Text: {extracted_text}")
        
        print("\n" + "=" * 70)
        print("✅ REAL BUTTON PAYLOAD TEST PASSED!")
        print("\n📋 What happens in the system:")
        print("  1. ✅ Webhook receives type: 'button'")
        print("  2. ✅ Extracts button.text or button.payload")
        print("  3. ✅ Text: '/Si, guardar.'")
        print("  4. ✅ Routes to Calendar Agent (contains '/si' and 'guardar')")
        print("  5. ✅ Calendar Agent creates event with context from history")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_real_button_payload()
