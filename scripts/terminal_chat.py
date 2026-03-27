import sys
from pathlib import Path
import asyncio
import unicodedata
from typing import Optional, List, Dict, Any

# Permite ejecutar este script directamente: `python3 scripts/terminal_chat.py`
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
	sys.path.insert(0, str(PROJECT_ROOT))

from agents.property_agent import property_agent
from agents.calendar_agent import calendar_agent


def _normalize_text(text: str) -> str:
	if not text:
		return ""
	text = text.strip().lower()
	text = unicodedata.normalize("NFKD", text)
	text = "".join(ch for ch in text if not unicodedata.combining(ch))
	return text


def _tokenize(text: str) -> set:
	clean = "".join(ch if ch.isalnum() or ch.isspace() else " " for ch in text)
	return set(clean.split())


def is_guardar_confirmation(message_text: str) -> bool:
	t = _normalize_text(message_text).lstrip("/").strip()
	tokens = _tokenize(t)
	return "guardar" in tokens and bool({"si", "ok", "dale", "confirmar", "confirmo"} & tokens)


def should_route_to_calendar(message_text: str, history: Optional[List[Dict[str, Any]]] = None) -> bool:
	t = _normalize_text(message_text).lstrip("/").strip()

	confirmations = {
		"si, guardar", "si guardar", "si", "ok", "dale", "confirmo", "confirmar"
	}
	calendar_keywords = (
		"agendar", "agenda", "agend", "evento", "calendario", "recordatorio",
		"cita", "turno", "reunion", "meeting"
	)

	if is_guardar_confirmation(t):
		return True

	if any(k in t for k in calendar_keywords):
		return True

	# Si el bot anterior habló de agenda/calendario, una respuesta afirmativa breve
	# también se envía al CalendarAgent.
	if t in confirmations and history:
		for item in reversed(history):
			if item.get("role") != "model":
				continue
			parts = item.get("parts", [])
			last_bot_text = parts[0] if isinstance(parts, list) and parts else ""
			last_bot_text = _normalize_text(str(last_bot_text))
			if any(k in last_bot_text for k in ("agendar", "agenda", "calendario", "turno")):
				return True
			break

	return t in {"si, guardar", "si guardar", "si agendar", "si, agendar"}


async def main():
	print("💬 Simulador terminal (escribí 'salir' para terminar)")
	history = []

	# Si llega '/si, guardar', mantener CalendarAgent por 1 mensaje adicional.
	calendar_sticky_turns = 0

	while True:
		user_text = input("\nUsuario: ").strip()
		if user_text.lower() in {"salir", "exit", "quit"}:
			print("👋 Fin.")
			break

		history.append({"role": "user", "parts": [user_text]})

		if calendar_sticky_turns > 0:
			route_to_calendar = True
			calendar_sticky_turns -= 1
		else:
			route_to_calendar = should_route_to_calendar(user_text, history=history)

		# Activa "sticky" cuando presionan el botón/template de guardar.
		if is_guardar_confirmation(user_text):
			calendar_sticky_turns = 1

		if route_to_calendar:
			reply = await calendar_agent.handle_message(user_text, history=history)
			agent_name = "CalendarAgent"
		else:
			reply = await property_agent.handle_message(user_text, history=history)
			agent_name = "PropertyAgent"

		print(f"{agent_name}: {reply}")
		history.append({"role": "model", "parts": [reply]})


if __name__ == "__main__":
	asyncio.run(main())
