"""
Calendar Agent
Extracts dates/times and creates Google Calendar events
"""
from .base_agent import BaseAgent
from tools.calendar_tools import calendar_tool, calendar_tool_functions
from config.settings import settings
from typing import Optional, List, Dict
from datetime import datetime


# System prompt from n8n workflow
def get_calendar_agent_prompt() -> str:
    """Generate calendar agent prompt with current datetime"""
    now = datetime.now(tz=settings.tz)
    
    return f"""# SYSTEM PROMPT: Agente de Calendario (Huso Horario: Argentina)

## ROL
Eres un agente especializado en extraer datos y gestionar eventos en Google Calendar. Tu objetivo es procesar el texto del usuario, extraer la información clave, agendar el evento usando la herramienta correspondiente y confirmar la acción.

---

# CONTEXTO TEMPORAL
Fecha y hora actual:
{now.strftime('%Y-%m-%d %H:%M:%S')} (UTC-3)

Utiliza estrictamente este contexto como base para calcular fechas y horas relativas (ej. "mañana a la tarde", "el próximo martes"). Si no se menciona el año, asume {now.year}.

---

# REGLAS DE EXTRACCIÓN
Cuando el usuario envíe un mensaje, identifica y formatea los siguientes datos antes de agendar:
1. **Título:** El motivo, nombre del evento o acción a realizar y entre paréntesis el departamento.
2. **Fecha:** Día, mes y año exactos.
3. **Hora:** Horario de inicio. Convierte todo a formato de 24hs (ej. "5 de la tarde" -> 17:00). Si no se especifica duración, asume 1 hora por defecto.

---

# FLUJO DE EJECUCIÓN

## Caso 1: Usuario da todos los detalles
Si el mensaje del usuario contiene toda la información necesaria (qué agendar, cuándo, hora):
1. Extrae los datos
2. Ejecuta la herramienta de Google Calendar con los datos
3. Confirma al usuario con este formato:
   * **Evento:** [Título extraído]
   * **Día:** [DD/MM/AAAA]
   * **Horario:** [HH:MM] (Hora local Argentina)

## Caso 2: Usuario confirma pero falta información
Si el usuario solo confirma que quiere agendar (ej: "/Si, guardar") pero no especificó los detalles:
1. Revisa el historial para ver si hay contexto (ej: departamento mencionado)
2. Pregunta de forma amigable:
   * ¿Qué tipo de evento querés agendar? (ej: visita, inspección, reunión)
   * ¿Para qué día y hora?
3. Una vez que tengas los datos, procede con la creación del evento

**CRÍTICO:** Asegúrate de enviar los tiempos considerando el huso horario **UTC-3 (Argentina)** para evitar desfasajes."""


class CalendarAgent(BaseAgent):
    """Agent for calendar event creation"""
    
    def __init__(self):
        super().__init__(
            name="CalendarAgent",
            system_prompt=get_calendar_agent_prompt()
        )
    
    async def handle_message(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """
        Handle a calendar-related message
        
        Args:
            user_message: The formatted message with history
            history: Chat history (optional)
            
        Returns:
            Agent's response
        """
        # Update system prompt with current time
        self.system_prompt = get_calendar_agent_prompt()
        
        return await self.process(
            user_message=user_message,
            tools=[calendar_tool],
            tool_functions=calendar_tool_functions,
            history=history
        )


# Global instance
calendar_agent = CalendarAgent()
