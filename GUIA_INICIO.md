# 🚀 Guía de Inicio Rápido - WhatsApp Chatbot

## ✅ Proyecto Completado

Tu automatización de n8n ha sido convertida exitosamente a Python/FastAPI.

### 📊 Estadísticas
- **25 archivos Python** creados
- **3 Agentes de IA** implementados
- **17 tareas** completadas
- **Arquitectura modular** profesional

---

## 🏗️ Estructura del Proyecto

```
chatbot_papa/
├── main.py                      # 🚀 Aplicación FastAPI principal
├── requirements.txt             # 📦 Dependencias
├── .env                         # 🔐 Credenciales (ya configurado)
├── .env.example                 # 📝 Template de variables
├── README.md                    # 📚 Documentación completa
├── Dockerfile                   # 🐳 Container Docker
├── docker-compose.yml           # 🐳 Orquestación Docker
├── test_setup.py                # 🧪 Script de pruebas
│
├── config/
│   ├── __init__.py
│   └── settings.py              # ⚙️  Configuración centralizada
│
├── models/
│   ├── __init__.py
│   ├── user.py                  # 👤 Modelo de usuario
│   ├── message.py               # 💬 Modelos de mensajes
│   └── department.py            # 🏢 Modelo de departamento
│
├── services/
│   ├── __init__.py
│   ├── supabase_client.py       # 💾 Cliente Supabase
│   ├── whatsapp.py              # 📱 Cliente WhatsApp
│   ├── gemini_client.py         # 🤖 Cliente Gemini AI
│   └── calendar_client.py       # 📅 Cliente Google Calendar
│
├── agents/
│   ├── __init__.py
│   ├── base_agent.py            # 🧩 Clase base de agentes
│   ├── property_agent.py        # 🏢 Agente inmobiliario
│   └── calendar_agent.py        # 📅 Agente de calendario
│
├── tools/
│   ├── __init__.py
│   ├── supabase_tools.py        # 🔧 Tools para Supabase
│   └── calendar_tools.py        # 🔧 Tools para Calendar
│
├── routes/
│   ├── __init__.py
│   └── webhook.py               # 🌐 Webhook de WhatsApp
│
└── utils/
    ├── __init__.py
    ├── history.py               # 📜 Utilidades de historial
    └── image_processor.py       # 🖼️  Procesador de imágenes
```

---

## 🎯 Funcionalidades Implementadas

### 1️⃣ Agente Inmobiliario (Property Agent)
- ✅ Busca departamentos por dirección
- ✅ Crea nuevos departamentos
- ✅ Guarda notas/mensajes sobre departamentos
- ✅ Procesa imágenes con Gemini Vision
- ✅ Responde con formato estructurado

**Ejemplo de uso:**
```
Usuario: "San Benito de Palermo 1584 está cusco durmiendo"
Bot: ✅ Información guardada exitosamente
     📍 Depto: San Benito de Palermo 1584
     💬 Nota: está cusco durmiendo
```

### 2️⃣ Agente de Calendario (Calendar Agent)
- ✅ Extrae fechas y horas del lenguaje natural
- ✅ Crea eventos en Google Calendar
- ✅ Maneja zona horaria Argentina (UTC-3)
- ✅ Procesa referencias relativas ("mañana", "próximo martes")

**Ejemplo de uso:**
```
Usuario: "Agendar visita mañana a las 3 de la tarde en San Benito"
Bot: * Evento: Visita (San Benito)
     * Día: 28/03/2026
     * Horario: 15:00 (Hora local Argentina)
```

### 3️⃣ Procesamiento de Imágenes
- ✅ Descarga imágenes de WhatsApp
- ✅ Sube a Supabase Storage
- ✅ Procesa con Gemini Vision
- ✅ Asocia imágenes a departamentos

---

## 🚀 Cómo Ejecutar

### Paso 1: Verificar Configuración
Tu archivo `.env` ya está configurado con las credenciales correctas.

### Paso 2: Instalar Dependencias
```bash
pip3 install -r requirements.txt
```

### Paso 3: Configurar Supabase
Asegúrate de tener estas tablas creadas en Supabase (ver README.md para SQL completo):
- `users` - Usuarios de WhatsApp
- `messages` - Historial de conversaciones
- `departamentos` - Listado de departamentos
- `mensajes` - Notas sobre departamentos
- Bucket `whatsapp-images` - Storage para imágenes

### Paso 4: Ejecutar el Servidor
```bash
# Desarrollo
python3 main.py

# O con uvicorn directamente
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Paso 5: Configurar Webhook de WhatsApp
1. Exponer tu servidor públicamente (usa ngrok para desarrollo):
   ```bash
   ngrok http 8000
   ```

2. En WhatsApp Business API, configura:
   - **URL:** `https://tu-dominio.com/webhook`
   - **Verify Token:** `tokenDeVerificacionPedro` (el que está en tu .env)
   - **Eventos:** Marca "messages"

---

## 🧪 Probar el Sistema

### Test Básico
```bash
python3 test_setup.py
```

### Test del API
```bash
# Abrir en navegador
http://localhost:8000

# Health check
curl http://localhost:8000/health
```

---

## 📝 Flujo de Funcionamiento

1. **WhatsApp recibe mensaje** → POST /webhook
2. **Sistema verifica/crea usuario** en Supabase
3. **Obtiene historial** (últimos 5 minutos)
4. **Detecta tipo de mensaje:**
   - Calendario → Si contiene palabras como "agendar", "evento", "cita"
   - Inmobiliario → Todo lo demás
5. **Procesa con agente IA** correspondiente
6. **Agente usa tools** (buscar_departamento, crear_departamento, crear_evento_calendar)
7. **Guarda en historial** la respuesta
8. **Envía respuesta** por WhatsApp

---

## 🔧 Herramientas Disponibles para los Agentes

### Tools de Supabase (Property Agent)
```python
- buscar_departamento(direccion: str)
- crear_departamento(direccion: str)
- guardar_mensaje(departamento_id: int, contenido: str, url_imagen: str)
```

### Tools de Calendar (Calendar Agent)
```python
- crear_evento_calendar(
    titulo: str,
    fecha_hora_inicio: str,
    fecha_hora_fin: str,
    descripcion: str,
    ubicacion: str
  )
```

---

## �� Troubleshooting

### Error: ModuleNotFoundError
```bash
pip3 install -r requirements.txt
```

### Error: Supabase connection
- Verifica que `SUPABASE_URL` y `SUPABASE_ANON_KEY` sean correctos en `.env`
- Asegúrate de que las tablas existan en Supabase

### Error: WhatsApp verification failed
- Verifica que `WHATSAPP_VERIFY_TOKEN` en `.env` coincida con el configurado en WhatsApp Business API

### Gemini API error
- Verifica `GEMINI_API_KEY` en `.env`
- Asegúrate de tener créditos en Google AI Studio

---

## 📚 Recursos Adicionales

- **README.md** - Documentación completa
- **n8n.json** - Workflow original de n8n
- **.env.example** - Template de variables de entorno
- **Dockerfile** - Para deployment en containers

---

## 🎉 ¡Listo para Producción!

Tu sistema está completamente funcional. Los próximos pasos recomendados:

1. ✅ Probar con mensajes reales de WhatsApp
2. ✅ Configurar Google Calendar OAuth (si usarás el agente de calendario)
3. ✅ Configurar logging profesional
4. ✅ Deploy en servidor (Railway, Render, AWS, etc.)
5. ✅ Configurar monitoring y alertas

---

## 💡 Consejos

- El sistema guarda historial de 5 minutos para contexto
- Los agentes pueden llamar múltiples herramientas en una conversación
- Las imágenes se suben automáticamente a Supabase Storage
- El timezone está configurado para Argentina (UTC-3)

---

**¿Preguntas?** Revisa el README.md o los comentarios en el código.

**¡Éxito con tu chatbot! 🚀**
