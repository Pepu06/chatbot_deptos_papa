"""
WhatsApp webhook endpoint
Handles incoming WhatsApp messages and verification
"""
from fastapi import APIRouter, Request, HTTPException, Query
from fastapi.responses import PlainTextResponse
from models import WhatsAppWebhook, WhatsAppMessage, UserCreate, MessageCreate
from services import supabase_service, whatsapp_service
from agents import property_agent, calendar_agent
from utils import create_user_message_with_history, process_whatsapp_image
from config.settings import settings
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_class=PlainTextResponse)
async def verify_webhook(
    hub_mode: str = Query(alias="hub.mode"),
    hub_verify_token: str = Query(alias="hub.verify_token"),
    hub_challenge: str = Query(alias="hub.challenge")
):
    """
    Webhook verification endpoint for WhatsApp
    WhatsApp will call this to verify the webhook
    """
    if hub_mode == "subscribe" and hub_verify_token == settings.whatsapp_verify_token:
        logger.info("✅ Webhook verified successfully")
        return hub_challenge
    else:
        logger.error("❌ Webhook verification failed")
        raise HTTPException(status_code=403, detail="Verification failed")


@router.post("/")
async def webhook(request: Request):
    """
    Main webhook endpoint for receiving WhatsApp messages
    """
    try:
        body = await request.json()
        webhook_data = WhatsAppWebhook(**body)
        logger.info(f"📩 POST recibido: {body}")  # <-- agregá esto
        
        # Process each entry and change
        for entry in webhook_data.entry:
            for change in entry.changes:
                if change.field == "messages" and change.value.messages:
                    for message_data in change.value.messages:
                        # Extract message info
                        wa_message = extract_whatsapp_message(message_data, change.value)
                        
                        # Process the message
                        await process_message(wa_message)
        
        return {"status": "ok"}
    
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        # Return 200 anyway to avoid WhatsApp retries
        return {"status": "error", "message": str(e)}


def extract_whatsapp_message(
    message_data,
    value
) -> WhatsAppMessage:
    """Extract WhatsApp message from webhook data"""
    contact_name = None
    if value.contacts and len(value.contacts) > 0:
        contact_name = value.contacts[0].profile.get("name")
    
    # Extract text or image info
    text = None
    image_id = None
    image_caption = None
    
    if message_data.type == "text" and message_data.text:
        text = message_data.text.body
    elif message_data.type == "image" and message_data.image:
        image_id = message_data.image.id
        image_caption = message_data.image.caption or ""
        text = image_caption  # Use caption as text
    elif message_data.type == "button" and message_data.button:
        # Handle button responses (template buttons)
        text = message_data.button.text or message_data.button.payload
        logger.info(f"📱 Button received: {text}")
    elif message_data.type == "interactive" and message_data.interactive:
        # Handle interactive messages (button replies, list replies, etc.)
        if message_data.interactive.type == "button_reply" and message_data.interactive.button_reply:
            # Use the button text as the message text
            text = message_data.interactive.button_reply.text or message_data.interactive.button_reply.payload
            logger.info(f"📱 Interactive button reply received: {text}")
    
    return WhatsAppMessage(
        wa_id=message_data.from_,
        message_id=message_data.id,
        timestamp=message_data.timestamp,
        message_type=message_data.type,
        text=text,
        image_id=image_id,
        image_caption=image_caption,
        contact_name=contact_name
    )


async def process_message(wa_message: WhatsAppMessage):
    """Process incoming WhatsApp message"""
    try:
        logger.info(f"📨 Processing message from {wa_message.wa_id}: {wa_message.text}")
        
        # 1. Get or create user
        user = await supabase_service.get_user(wa_message.wa_id)
        
        if not user:
            logger.info(f"👤 Creating new user: {wa_message.wa_id}")
            user = await supabase_service.create_user(
                UserCreate(
                    id=wa_message.wa_id,
                    name=wa_message.contact_name,
                    phone=wa_message.wa_id
                )
            )
            
            # Send welcome message
            await whatsapp_service.send_message(
                to=wa_message.wa_id,
                message="¡Hola! Bienvenido al sistema de gestión inmobiliaria. ¿En qué puedo ayudarte?"
            )
        
        # 2. Add incoming message to history
        image_url = None
        if wa_message.image_id:
            # Process image
            image_url = await process_whatsapp_image(
                media_id=wa_message.image_id,
                user_id=wa_message.wa_id
            )
        
        await supabase_service.add_history(
            MessageCreate(
                user_id=wa_message.wa_id,
                content=wa_message.text or "[Imagen sin caption]",
                role="user",
                url_imagen=image_url
            )
        )
        
        # 3. Get conversation history (last 5 minutes)
        history = await supabase_service.get_history(wa_message.wa_id, minutes=5)
        
        # 4. Determine which agent to use
        # Check if message is about calendar/scheduling
        calendar_keywords = ["agendar", "calendario", "recordatorio", "evento", "cita", "reunión"]
        message_lower = (wa_message.text or "").lower()
        
        # Check if it's a button response from template (confirmation to schedule)
        is_calendar_confirmation = "/si" in message_lower and "guardar" in message_lower
        
        is_calendar_request = is_calendar_confirmation or any(keyword in message_lower for keyword in calendar_keywords)
        
        # 5. Format message with history
        user_message_with_history = create_user_message_with_history(
            current_message=wa_message.text or "[Imagen]",
            history=history[:-1]  # Exclude the message we just added
        )
        
        # 6. Process with appropriate agent
        if is_calendar_request:
            logger.info("📅 Using Calendar Agent")
            response = await calendar_agent.handle_message(user_message_with_history)
        else:
            logger.info("🏢 Using Property Agent")
            # Check if has image
            if wa_message.image_id and image_url:
                # Download image for Gemini
                image_data = await whatsapp_service.download_media(wa_message.image_id)
                response = await property_agent.handle_message(
                    user_message_with_history,
                    image_data=image_data
                )
            else:
                response = await property_agent.handle_message(user_message_with_history)
        
        # 7. Add assistant response to history
        await supabase_service.add_history(
            MessageCreate(
                user_id=wa_message.wa_id,
                content=response,
                role="assistant"
            )
        )
        
        # 8. Send response to user
        # Check if response indicates successful save (contains "✅" and "guardada")
        if "✅" in response and ("guardada" in response.lower() or "guardado" in response.lower()):
            # Send response first
            await whatsapp_service.send_message(
                to=wa_message.wa_id,
                message=response
            )
            # Then send template to offer calendar scheduling
            # Template has a quick reply button, no variables needed
            logger.info("📋 Sending template 'recordatorio_de_turno' with button")
            await whatsapp_service.send_template(
                to=wa_message.wa_id,
                template_name="recordatorio_de_turno",
                language_code="es_AR",  # Spanish (Argentina)
                components=None  # No variables, button is defined in template
            )
        else:
            # Regular message response
            await whatsapp_service.send_message(
                to=wa_message.wa_id,
                message=response
            )
        
        logger.info(f"✅ Message processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error in process_message: {e}")
        # Try to send error message to user
        try:
            await whatsapp_service.send_message(
                to=wa_message.wa_id,
                message="Disculpa, hubo un error procesando tu mensaje. Por favor intenta nuevamente."
            )
        except:
            pass
