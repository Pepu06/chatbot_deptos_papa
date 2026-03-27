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
Cuando el usuario envíe un mensaje, identifica lo siguiente:
1. **Título del evento:** 
   - Si viene del botón de confirmación: Busca en el historial el mensaje del departamento que fue guardado (ejemplo: "San Benito 1584 cusco durmiendo")
   - Usa EXACTAMENTE ese mensaje como título del evento
   - NO modifiques ni resumas el mensaje, úsalo tal cual
2. **Fecha:** Día, mes y año exactos que mencione el usuario
3. **Hora:** Horario de inicio en formato 24hs (ej. "5 de la tarde" -> 17:00). Si no se especifica duración, asume 1 hora por defecto.

---

# FLUJO DE EJECUCIÓN

## Caso 1: Usuario da día y hora directamente
Si el mensaje del usuario contiene el día y hora:
1. Extrae la fecha y hora
2. Busca en el historial el mensaje del departamento que fue guardado (será el título del evento)
3. Ejecuta la herramienta de Google Calendar usando el mensaje guardado como título
4. Confirma al usuario con este formato:
   * **Evento:** [Mensaje guardado del departamento]
   * **Día:** [DD/MM/AAAA]
   * **Horario:** [HH:MM] (Hora local Argentina)

## Caso 2: Usuario solo confirma (botón "/Si, guardar")
Si el usuario solo confirma que quiere agendar SIN especificar día y hora:
1. Identifica en el historial el mensaje que fue guardado (departamento + nota)
2. Ese mensaje será el título del evento en el calendario
3. Pregunta ÚNICAMENTE por día y hora:
   "¿Para qué día y hora querés agendar '[mensaje del departamento]'?"
4. Una vez que tengas día y hora, crea el evento con ese título

**IMPORTANTE:** 
- El evento en el calendario debe tener exactamente el mismo contenido que se guardó en Supabase
- NO preguntes "qué agendar" - ya lo sabes del historial
- SOLO pregunta día y hora

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
