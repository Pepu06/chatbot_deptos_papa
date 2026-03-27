"""
Test para verificar que "/Si, guardar" activa el Calendar Agent
"""

# Simular la lógica de detección del calendario
def should_use_calendar_agent(message_text):
    """
    Replica la lógica de routes/webhook.py para determinar
    si un mensaje debe ir al Calendar Agent
    """
    calendar_keywords = ["agendar", "calendario", "recordatorio", "evento", "cita", "reunión"]
    message_lower = (message_text or "").lower()
    
    # Check if it's a button response from template (confirmation to schedule)
    is_calendar_confirmation = "/si" in message_lower and "guardar" in message_lower
    
    is_calendar_request = is_calendar_confirmation or any(keyword in message_lower for keyword in calendar_keywords)
    
    return is_calendar_request


# Tests
print("🧪 Testing Calendar Agent Routing Logic")
print("=" * 70)

test_cases = [
    # Botón del template
    ("/Si, guardar", True, "Botón del template - DEBE ir a Calendar"),
    ("/si, guardar", True, "Botón en minúsculas - DEBE ir a Calendar"),
    ("Si, guardar", True, "Sin slash - DEBE ir a Calendar"),
    
    # Mensajes de calendario normales
    ("Agendar visita mañana", True, "Mensaje con 'agendar' - DEBE ir a Calendar"),
    ("Crear evento para el martes", True, "Mensaje con 'evento' - DEBE ir a Calendar"),
    ("Recordatorio para mañana", True, "Mensaje con 'recordatorio' - DEBE ir a Calendar"),
    
    # Mensajes de property (no calendario)
    ("Formosa 380 todo ok", False, "Mensaje de departamento - DEBE ir a Property"),
    ("San Benito 1584 cusco durmiendo", False, "Mensaje de departamento - DEBE ir a Property"),
    ("Guardar esto", False, "Solo 'guardar' sin '/si' - DEBE ir a Property"),
]

all_passed = True

for message, expected_calendar, description in test_cases:
    result = should_use_calendar_agent(message)
    status = "✅" if result == expected_calendar else "❌"
    agent = "Calendar" if result else "Property"
    
    if result != expected_calendar:
        all_passed = False
    
    print(f"{status} '{message}'")
    print(f"   → Goes to: {agent} Agent")
    print(f"   → {description}")
    print()

print("=" * 70)
if all_passed:
    print("✅ ALL TESTS PASSED!")
    print("\n🎉 El botón '/Si, guardar' ahora activa correctamente el Calendar Agent")
else:
    print("❌ SOME TESTS FAILED")
    print("\n⚠️  Revisa la lógica de routing")
