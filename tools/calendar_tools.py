"""
Google Calendar tools for Gemini function calling
Tools that the AI agents can use to create calendar events
"""
from google.generativeai.types import FunctionDeclaration, Tool
from services.calendar_client import calendar_service
from typing import Dict, Any
from datetime import datetime
import asyncio


# Function declaration for Gemini
crear_evento_calendar_declaration = FunctionDeclaration(
    name="crear_evento_calendar",
    description="Crea un evento en Google Calendar. Úsala cuando el usuario solicite agendar algo. Los tiempos deben estar en formato ISO 8601 con zona horaria UTC-3 (Argentina).",
    parameters={
        "type": "object",
        "properties": {
            "titulo": {
                "type": "string",
                "description": "Título/nombre del evento. Incluye el departamento entre paréntesis si aplica."
            },
            "fecha_hora_inicio": {
                "type": "string",
                "description": "Fecha y hora de inicio en formato ISO 8601. Ejemplo: '2024-03-15T17:00:00-03:00' (5 PM hora Argentina)"
            },
            "fecha_hora_fin": {
                "type": "string",
                "description": "Fecha y hora de fin en formato ISO 8601 (opcional, si no se provee se asume 1 hora de duración)"
            },
            "descripcion": {
                "type": "string",
                "description": "Descripción adicional del evento (opcional)"
            },
            "ubicacion": {
                "type": "string",
                "description": "Ubicación del evento (opcional)"
            }
        },
        "required": ["titulo", "fecha_hora_inicio"]
    }
)

# Tool object with calendar function
calendar_tool = Tool(
    function_declarations=[crear_evento_calendar_declaration]
)


# Actual Python function
def crear_evento_calendar(
    titulo: str,
    fecha_hora_inicio: str,
    fecha_hora_fin: str = None,
    descripcion: str = None,
    ubicacion: str = None
) -> Dict[str, Any]:
    """Create a calendar event"""
    print(f"🔧 crear_evento_calendar llamada:")
    print(f"   Título: {titulo}")
    print(f"   Inicio: {fecha_hora_inicio}")
    print(f"   Fin: {fecha_hora_fin}")
    
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            print("   ⚙️ Loop running - usando ThreadPoolExecutor")
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    calendar_service.create_event(
                        title=titulo,
                        start_datetime=fecha_hora_inicio,
                        end_datetime=fecha_hora_fin,
                        description=descripcion,
                        location=ubicacion
                    )
                )
                event = future.result()
        else:
            print("   ⚙️ Loop not running - usando run_until_complete")
            event = loop.run_until_complete(
                calendar_service.create_event(
                    title=titulo,
                    start_datetime=fecha_hora_inicio,
                    end_datetime=fecha_hora_fin,
                    description=descripcion,
                    location=ubicacion
                )
            )
        
        if event:
            print(f"   ✅ Evento creado: {event.get('id')}")
            return {
                "creado": True,
                "evento": {
                    "id": event.get("id"),
                    "titulo": event.get("summary"),
                    "inicio": event.get("start", {}).get("dateTime"),
                    "fin": event.get("end", {}).get("dateTime"),
                    "link": event.get("htmlLink")
                },
                "mensaje": "Evento creado exitosamente en Google Calendar"
            }
        else:
            print("   ❌ Event es None")
            return {
                "creado": False,
                "error": "No se pudo crear el evento en el calendario"
            }
    except Exception as e:
        print(f"   ❌ Excepción: {e}")
        import traceback
        traceback.print_exc()
        return {
            "creado": False,
            "error": str(e)
        }


# Dictionary mapping function names to actual functions
calendar_tool_functions = {
    "crear_evento_calendar": crear_evento_calendar
}
