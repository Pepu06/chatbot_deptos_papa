"""
Test para verificar que el fix del botón de calendario funciona correctamente
"""

def test_calendar_routing():
    """Test the calendar routing logic with various button formats"""
    
    # Simular la lógica NUEVA de routing
    def should_route_to_calendar(message_text):
        calendar_keywords = ["agendar", "calendario", "recordatorio", "evento", "cita", "reunión"]
        message_lower = (message_text or "").lower().strip()
        
        # Nueva lógica mejorada
        is_calendar_confirmation = (
            ("/si" in message_lower or "/sí" in message_lower or message_lower.startswith("si")) and 
            "guardar" in message_lower
        )
        
        is_calendar_request = is_calendar_confirmation or any(keyword in message_lower for keyword in calendar_keywords)
        
        return is_calendar_request
    
    # Test cases
    test_cases = [
        # Button variations
        ("/Si, guardar", True, "Botón con slash y mayúscula"),
        ("/si, guardar", True, "Botón con slash y minúscula"),
        ("/Sí, guardar", True, "Botón con slash y acento"),
        ("Si, guardar", True, "Botón sin slash"),
        (" /Si, guardar ", True, "Botón con espacios extra"),
        
        # Direct calendar requests  
        ("agendar visita mañana", True, "Mensaje directo con 'agendar'"),
        ("crear un evento", True, "Mensaje directo con 'evento'"),
        ("recordatorio para el martes", True, "Mensaje directo con 'recordatorio'"),
        
        # Property messages (should NOT go to calendar)
        ("San Benito 1584 todo ok", False, "Mensaje de departamento"),
        ("guardar esta información", False, "Solo 'guardar' sin contexto de calendario"),
        ("Formosa 380 cusco durmiendo", False, "Mensaje de estado de departamento"),
    ]
    
    print("🧪 Test: Calendar Button Routing Fix")
    print("=" * 80)
    
    all_passed = True
    for message, should_be_calendar, description in test_cases:
        result = should_route_to_calendar(message)
        passed = result == should_be_calendar
        status = "✅" if passed else "❌"
        agent = "CALENDAR" if result else "PROPERTY"
        
        if not passed:
            all_passed = False
        
        print(f"{status} '{message}'")
        print(f"   → Ruteado a: {agent} Agent")
        print(f"   → Esperado: {'CALENDAR' if should_be_calendar else 'PROPERTY'} Agent")
        print(f"   → {description}")
        print()
    
    print("=" * 80)
    if all_passed:
        print("✅ TODOS LOS TESTS PASARON!")
        print("\n🎉 El fix del botón de calendario funciona correctamente")
        return True
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print("\n⚠️  Revisa la lógica de routing")
        return False


if __name__ == "__main__":
    success = test_calendar_routing()
    exit(0 if success else 1)
