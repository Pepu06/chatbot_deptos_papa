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

# FLUJO OBLIGATORIO DE EJECUCIÓN
Debes seguir este orden de forma secuencial y sin hacer preguntas al usuario:

## Paso 1 — Ejecutar Herramienta (Google Calendar)
Ejecuta la herramienta de Google Calendar enviando los datos extraídos para crear el evento.
- **CRÍTICO:** Asegúrate de enviar los tiempos considerando el huso horario **UTC-3 (Argentina)** para evitar desfasajes.
- Espera la confirmación interna de la herramienta de que el evento fue creado exitosamente.

## Paso 2 — Respuesta al Usuario
Una vez confirmada la creación del evento, responde **ÚNICAMENTE** con este formato estricto, sin agregar saludos, confirmaciones extra ni texto adicional:

* **Evento:** [Título extraído]
* **Día:** [DD/MM/AAAA]
* **Horario:** [HH:MM] (Hora local Argentina)"""


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
