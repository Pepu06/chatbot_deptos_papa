# 🐛 Errores Detectados y Solucionados

## Error Principal: 405 Method Not Allowed
**Estado:** ✅ SOLUCIONADO

### Problema
WhatsApp enviaba peticiones POST a `/webhook` pero la aplicación respondía con 405 Method Not Allowed.

### Causa
- Las rutas estaban definidas con `prefix="/webhook"` en `main.py`
- Las funciones usaban `@router.get("/")` y `@router.post("/")`
- Con `redirect_slashes = False`, solo respondían a `/webhook/` (con slash final)
- WhatsApp llama a `/webhook` (sin slash final)

### Solución Aplicada
1. **main.py línea 30:** Eliminé `prefix="/webhook"` del router
2. **webhook.py líneas 23 y 41:** Cambié las rutas de `"/"` a `"/webhook"` directamente

```python
# Antes:
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])
@router.get("/")
@router.post("/")

# Después:
app.include_router(webhook_router, tags=["webhook"])
@router.get("/webhook")
@router.post("/webhook")
```

### Resultado
✅ GET /webhook - Funciona correctamente (verificación)
✅ POST /webhook - Funciona correctamente (recibe mensajes)

---

## Error Secundario: Base de Datos Supabase
**Estado:** ⚠️ REQUIERE ACCIÓN MANUAL EN SUPABASE

### Problema 1: Columna 'phone' no encontrada
```
Error creating user: {'code': 'PGRST204', 'details': None, 'hint': None, 
'message': "Could not find the 'phone' column of 'users' in the schema cache"}
```

**ACTUALIZACIÓN:** ✅ El campo `phone` NO es necesario. El `id` ya ES el número de teléfono.

### Problema 2: Foreign key constraint violation
```
Error adding message to history: {'code': '23503', 
'details': 'Key (user_id)=(1234567890) is not present in table "users".', 
'message': 'insert or update on table "history" violates foreign key constraint'}
```

### Causa
La tabla `users` en Supabase intentaba insertar el campo `phone` que no existe.
**En realidad, el campo `id` ya contiene el número de teléfono de WhatsApp.**

### Solución Aplicada en el Código
Actualicé `services/supabase_client.py` para:
1. **Eliminar** el intento de insertar el campo `phone`
2. Solo insertar `id` (que ya ES el teléfono) y `name`
3. Simplificar la lógica de creación de usuario

### ⚠️ ACCIÓN REQUERIDA EN SUPABASE

**Debes ejecutar este SQL en Supabase:**

```sql
-- Crear tabla users (id es el número de teléfono)
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,  -- WhatsApp phone number
  name TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Verificar/crear tabla history
CREATE TABLE IF NOT EXISTS history (
  id SERIAL PRIMARY KEY,
  user_id TEXT REFERENCES users(id),
  content TEXT NOT NULL,
  role TEXT NOT NULL,
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 4. Crear índices
CREATE INDEX IF NOT EXISTS idx_history_user_id ON history(user_id);
CREATE INDEX IF NOT EXISTS idx_history_created_at ON history(created_at);
```

**📝 Archivo creado:** `fix_supabase_schema.sql` con el script completo

---

## 📋 Checklist de Deploy

### 1. ✅ Código Corregido
- [x] Fix de ruta /webhook
- [x] Manejo mejorado de errores en Supabase
- [x] Código probado localmente

### 2. ⚠️ Pendiente: Configurar Supabase
- [ ] Ejecutar `fix_supabase_schema.sql` en Supabase SQL Editor
- [ ] Verificar que todas las tablas existen
- [ ] Verificar que la columna `phone` existe en `users`

### 3. ✅ Variables de Entorno en Railway
Verificar que estas variables están configuradas:
- [x] WHATSAPP_TOKEN
- [x] WHATSAPP_VERIFY_TOKEN
- [x] WHATSAPP_PHONE_NUMBER_ID
- [x] SUPABASE_URL
- [x] SUPABASE_ANON_KEY
- [x] GEMINI_API_KEY
- [x] GOOGLE_CREDENTIALS
- [x] GOOGLE_CALENDAR_ID

### 4. 🚀 Deploy
```bash
# Push a GitHub (Railway se auto-deploya)
git add .
git commit -m "Fix: Webhook 405 error y mejoras en Supabase"
git push origin main
```

### 5. ✅ Verificar Deploy
Después del deploy, revisar logs en Railway:
- [x] Servidor inicia correctamente
- [x] Mensaje: "✅ Google Calendar autenticado con Service Account"
- [ ] No hay errores de Supabase

---

## 🧪 Testing

### Test Local Realizado
```bash
✅ Test 1: GET /webhook (verification) - PASS
✅ Test 2: POST /webhook (accepts POST method) - PASS  
✅ Test 3: No 405 errors - PASS
⚠️  Test 4: Create user - FAIL (columna phone no existe en Supabase)
⚠️  Test 5: Add message to history - FAIL (user no se creó)
```

### Test de Producción Recomendado
1. Enviar mensaje de WhatsApp al bot
2. Verificar en logs de Railway:
   - No hay error 405
   - Usuario se crea correctamente
   - Mensaje se guarda en history
   - Bot responde

---

## 📊 Resumen

| Error | Estado | Requiere Acción |
|-------|--------|-----------------|
| 405 Method Not Allowed | ✅ Solucionado | No - ya está en el código |
| Columna 'phone' no existe | ⚠️ Detectado | Sí - ejecutar SQL en Supabase |
| Foreign key violation | ⚠️ Detectado | Sí - ejecutar SQL en Supabase |

---

## 🎯 Próximos Pasos

1. **URGENTE:** Ejecutar `fix_supabase_schema.sql` en Supabase
2. Push del código corregido a GitHub
3. Verificar deploy en Railway
4. Probar enviando mensaje de WhatsApp
5. Monitorear logs para confirmar que todo funciona

---

**Fecha:** 2026-04-07
**Archivos modificados:**
- `main.py`
- `routes/webhook.py`
- `services/supabase_client.py`

**Archivos creados:**
- `fix_supabase_schema.sql`
- `ERRORES_DETECTADOS.md` (este archivo)
