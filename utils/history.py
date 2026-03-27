"""
History utilities
Format and filter conversation history for AI agents
"""
from models import Message
from typing import List
from datetime import datetime


def format_history_for_gemini(messages: List[Message]) -> str:
    """
    Format message history for Gemini prompt
    Sorted oldest to newest
    
    Args:
        messages: List of Message objects sorted by created_at ascending
        
    Returns:
        Formatted history string
    """
    if not messages:
        return "No hay historial previo."
    
    history_lines = []
    for msg in messages:
        role_label = "Usuario" if msg.role == "user" else "Asistente"
        
        # Include image info if present
        if msg.url_imagen:
            history_lines.append(f"{role_label}: {msg.content} [Imagen: {msg.url_imagen}]")
        else:
            history_lines.append(f"{role_label}: {msg.content}")
    
    return "\n".join(history_lines)


def format_history_with_image(messages: List[Message]) -> str:
    """
    Format history specifically for messages with images
    
    Args:
        messages: List of Message objects
        
    Returns:
        Formatted history string
    """
    return format_history_for_gemini(messages)


def create_user_message_with_history(
    current_message: str,
    history: List[Message]
) -> str:
    """
    Create a complete user message with conversation history
    
    Args:
        current_message: The current message from user
        history: Previous messages
        
    Returns:
        Formatted message with history context
    """
    history_text = format_history_for_gemini(history)
    
    return f"""Este es el historial de mensajes de los últimos 5 minutos, está ordenado de arriba lo más viejo, abajo lo más nuevo:
{history_text}

Mensaje actual del usuario: {current_message}"""
