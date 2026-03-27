# WhatsApp Chatbot con IA - FastAPI

Bot de WhatsApp con Google Gemini para gestión inmobiliaria y calendario.

## 🌟 Características

- 🤖 **3 Agentes de IA** con Google Gemini
  - Agente de gestión inmobiliaria (búsqueda y gestión de departamentos)
  - Agente de calendario (creación de eventos en Google Calendar)
  - Soporte para procesamiento de imágenes
  
- 💾 **Base de datos Supabase**
  - Gestión de usuarios
  - Historial de conversaciones
  - Gestión de departamentos
  - Almacenamiento de imágenes

- 📱 **WhatsApp Business API**
  - Recepción de mensajes (texto e imágenes)
  - Envío de respuestas
  - Webhook verification

## 🏗️ Arquitectura

```
fastapi-whatsapp-bot/
├── main.py                    # App FastAPI principal
├── config/                    # Configuración
├── models/                    # Modelos Pydantic
├── services/                  # Servicios (Supabase, WhatsApp, Gemini, Calendar)
├── agents/                    # Agentes de IA
├── tools/                     # Herramientas para Gemini (function calling)
├── routes/                    # Endpoints FastAPI
└── utils/                     # Utilidades
```

## 🚀 Setup

### 1. Requisitos

- Python 3.9+
- Cuenta de WhatsApp Business API
- Proyecto Supabase
- Google Gemini API key
- Google Calendar API (opcional)

### 2. Instalación

```bash
# Instalar dependencias
pip install -r requirements.txt
```

### 3. Configuración

Copia `.env.example` a `.env` y configura tus credenciales:

```bash
cp .env.example .env
```

Edita `.env` con tus credenciales reales.

### 4. Configurar Supabase

Crea las siguientes tablas en Supabase:

```sql
-- Tabla de usuarios
CREATE TABLE users (
  id TEXT PRIMARY KEY,
  name TEXT,
  phone TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de historial de mensajes
CREATE TABLE history (
  id SERIAL PRIMARY KEY,
  user_id TEXT REFERENCES users(id),
  content TEXT NOT NULL,
  role TEXT NOT NULL, -- 'user' o 'assistant'
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de departamentos
CREATE TABLE departamentos (
  id SERIAL PRIMARY KEY,
  address TEXT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Tabla de mensajes sobre departamentos
CREATE TABLE mensajes (
  id SERIAL PRIMARY KEY,
  departamento_id INTEGER REFERENCES departamentos(id),
  content TEXT NOT NULL,
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Índices para mejor performance
CREATE INDEX idx_history_user_id ON history(user_id);
CREATE INDEX idx_history_created_at ON history(created_at);
CREATE INDEX idx_departamentos_address ON departamentos(address);
```

También crea un bucket de storage llamado `whatsapp-images` para las imágenes.

### 5. Google Calendar (Opcional)

Si usarás el agente de calendario:

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un proyecto y habilita Google Calendar API
3. Crea credenciales OAuth 2.0
4. Descarga el archivo `credentials.json`
5. Ejecuta el flujo de autenticación inicial (se creará `token.json`)

## 🏃 Ejecutar

### Desarrollo

```bash
python main.py
```

O con uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Producción

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

O con Docker:

```bash
docker-compose up -d
```

## 🔗 Configurar Webhook de WhatsApp

1. Ejecuta tu servidor (debe ser accesible públicamente)
2. Usa ngrok para desarrollo:
   ```bash
   ngrok http 8000
   ```
3. En WhatsApp Business API, configura el webhook:
   - URL: `https://tu-dominio.com/webhook`
   - Verify Token: el valor de `WHATSAPP_VERIFY_TOKEN` en tu `.env`
   - Marca "messages" en los eventos

## 📖 Uso

### Conversación Normal (Gestión Inmobiliaria)

Usuario: "San Benito de Palermo 1584 está cusco durmiendo"

Bot:
- Busca el departamento
- Si no existe, pregunta si crear
- Guarda la nota
- Confirma con emojis

### Crear Evento en Calendario

Usuario: "Agendar visita mañana a las 3 de la tarde en San Benito de Palermo"

Bot:
- Extrae fecha/hora
- Crea evento en Google Calendar
- Confirma con detalles

### Mensaje con Imagen

Usuario: [Envía imagen con caption "San Benito 1584 - problema en la cocina"]

Bot:
- Descarga imagen
- Sube a Supabase
- Procesa con Gemini Vision
- Guarda nota con URL de imagen

## 🛠️ API Endpoints

- `GET /` - Health check
- `GET /health` - Detailed health check
- `GET /webhook` - Webhook verification (WhatsApp)
- `POST /webhook` - Recibir mensajes de WhatsApp

## 📝 Logs

Los logs se imprimen en consola. Para producción, configura logging apropiado:

```python
import logging
logging.basicConfig(level=logging.INFO)
```

## 🐛 Debugging

- Revisa los logs de consola
- Verifica que las credenciales sean correctas
- Asegúrate que las tablas de Supabase existan
- Verifica que el webhook esté correctamente configurado

## 📄 Licencia

MIT
# chatbot_deptos_papa
