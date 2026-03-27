# 🚀 Instrucciones de Deploy - Fix Calendario

## ✅ Estado Actual
- Código corregido y probado ✓
- Evento de prueba creado exitosamente en alquileresdgs@gmail.com ✓
- Listo para deploy a producción ✓

## 📋 Pasos para Deploy

### 1. Push a GitHub
```bash
git push origin main
```

### 2. Configurar Variable en Railway

**IMPORTANTE:** Debes agregar esta variable de entorno en Railway:

```
GOOGLE_CALENDAR_ID=alquileresdgs@gmail.com
```

**Cómo hacerlo:**
1. Ve a tu proyecto en Railway
2. Click en "Variables"
3. Agrega nueva variable:
   - Name: `GOOGLE_CALENDAR_ID`
   - Value: `alquileresdgs@gmail.com`
4. Click "Add" y la app se reiniciará automáticamente

### 3. Verificar Deploy

Después del deploy, revisa los logs en Railway. Deberías ver:

```
✅ Google Calendar autenticado con Service Account
```

Si ves ese mensaje, la autenticación funcionó.

### 4. Probar en WhatsApp

**Flujo completo:**

1. Envía: `Formosa 380 probando calendario`
2. Bot responde:
   ```
   ✅ Información guardada
   📍 Depto: Formosa 380
   💬 Nota: probando calendario
   
   ¿Querés agendar algo en el calendario para este departamento?
   ```
3. Bot envía template con botón "Sí, agendar"
4. Presiona el botón
5. Bot responde:
   ```
   ¿Para qué día y hora querés agendar 'Formosa 380 probando calendario'?
   ```
6. Responde: `mañana a las 3 de la tarde`
7. **Resultado esperado:**
   ```
   * Evento: Formosa 380 probando calendario
   * Día: 28/03/2026
   * Horario: 15:00 (Hora local Argentina)
   ```
8. **Verifica en Google Calendar** (alquileresdgs@gmail.com) que el evento se creó

## 🔍 Logs a Buscar

Si algo falla, busca en los logs:

### ✅ Logs correctos:
```
✅ Google Calendar autenticado con Service Account
📱 Interactive button reply received: '/Si, guardar'
🔍 is_calendar_request: True
📅 Using Calendar Agent
🔧 AI calling function: crear_evento_calendar
✅ Event created: https://calendar.google.com/...
```

### ❌ Errores comunes:

**Error 1:** `name 'json' is not defined`
- **Solución:** Ya corregido en el código

**Error 2:** `settings.GOOGLE_CREDENTIALS not found`
- **Solución:** Ya corregido en el código

**Error 3:** Evento se crea pero no aparece en el calendario
- **Causa:** Falta `GOOGLE_CALENDAR_ID` en Railway
- **Solución:** Agregar la variable como se indica en el paso 2

## 📝 Resumen de Cambios

### Archivos modificados:
1. `routes/webhook.py` - Routing mejorado
2. `agents/calendar_agent.py` - Usa mensaje exacto de Supabase
3. `services/calendar_client.py` - Imports agregados
4. `config/settings.py` - Variable google_credentials

### Variables de entorno requeridas:
- `GOOGLE_CREDENTIALS` - JSON de service account (ya existía)
- `GOOGLE_CALENDAR_ID` - Email del calendario (**NUEVA - agregar en Railway**)

---

**¿Todo listo?** Ejecuta `git push origin main` y agrega la variable en Railway 🚀
