#!/bin/bash
# Correr este script desde la raíz del repo clonado (chatbot_deptos_papa/)
# Aplica todos los cambios de migración Supabase → PostgreSQL Railway

set -e

echo "✅ Aplicando cambios..."

# ── requirements.txt ──────────────────────────────────────────────────────────
cat > requirements.txt << 'HEREDOC'
# FastAPI and server
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-multipart==0.0.12

# Environment and config
python-dotenv==1.0.1
pydantic==2.9.2
pydantic-settings==2.6.1

# Database
psycopg2-binary==2.9.10

# Google services
google-generativeai==0.8.3
google-auth==2.35.0
google-auth-oauthlib==1.2.1
google-api-python-client==2.149.0

# HTTP client
httpx==0.27.2

# Utilities
pytz==2024.2
python-dateutil==2.9.0.post0

# Image processing (optional)
Pillow==11.0.0
HEREDOC

# ── config/settings.py ────────────────────────────────────────────────────────
cat > config/settings.py << 'HEREDOC'
"""
Configuration settings using Pydantic
Loads environment variables and validates configuration
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # WhatsApp Business API
    whatsapp_client_id: Optional[str] = None
    whatsapp_token: str
    whatsapp_verify_token: str = "my_verify_token_123"
    whatsapp_phone_number_id: Optional[str] = None
    whatsapp_api_url: str = "https://graph.facebook.com/v21.0"

    # PostgreSQL (Railway provee DATABASE_URL automáticamente)
    database_url: str

    # Supabase (deprecado — se migró a PostgreSQL en Railway)
    supabase_url: Optional[str] = None
    supabase_anon_key: Optional[str] = None
    supabase_service_key: Optional[str] = None

    # Google Gemini
    gemini_api_key: str
    gemini_model: str = "gemini-2.0-flash-exp"

    # Google Calendar
    google_credentials: str  # Service Account credentials JSON
    google_calendar_id: str = "primary"

    # Legacy OAuth fields (deprecated, usar google_credentials)
    google_calendar_client_id: Optional[str] = None
    google_calendar_client_secret: Optional[str] = None
    google_calendar_redirect_uri: str = "http://localhost:8000/auth/callback"
    google_calendar_token_file: str = "token.json"

    # Application
    timezone: str = "America/Argentina/Buenos_Aires"
    debug: bool = True

    @property
    def tz(self):
        """Get timezone object"""
        import pytz
        return pytz.timezone(self.timezone)

    @property
    def TIMEZONE(self):
        return self.timezone

    @property
    def DEBUG(self):
        return self.debug

    @property
    def GEMINI_MODEL(self):
        return self.gemini_model

    @property
    def GOOGLE_CREDENTIALS(self):
        return self.google_credentials


# Global settings instance
settings = Settings()
HEREDOC

# ── services/supabase_client.py ───────────────────────────────────────────────
cat > services/supabase_client.py << 'HEREDOC'
"""
PostgreSQL database client
Usa tablas chatbot_* para usuarios/historial y propiedad_actualizaciones para mensajes.
"""
import uuid
import psycopg2
import psycopg2.pool
import psycopg2.extras
from config.settings import settings
from models import User, UserCreate, Message, MessageCreate, Department, DepartmentCreate
from typing import List, Optional
from datetime import datetime, timedelta


class SupabaseService:
    """Database service backed by PostgreSQL (Railway)"""

    def __init__(self):
        self._pool: Optional[psycopg2.pool.ThreadedConnectionPool] = None

    def _get_pool(self) -> psycopg2.pool.ThreadedConnectionPool:
        if self._pool is None:
            self._pool = psycopg2.pool.ThreadedConnectionPool(
                1, 10,
                settings.database_url,
                cursor_factory=psycopg2.extras.RealDictCursor
            )
        return self._pool

    def _acquire(self):
        return self._get_pool().getconn()

    def _release(self, conn):
        self._get_pool().putconn(conn)

    # ------------------------------------------------------------------ #
    # Users  →  chatbot_users
    # ------------------------------------------------------------------ #

    async def get_user(self, user_id: str) -> Optional[User]:
        conn = self._acquire()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT * FROM chatbot_users WHERE id = %s", (user_id,))
                row = cur.fetchone()
                if row:
                    return User(**dict(row))
                return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
        finally:
            self._release(conn)

    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        conn = self._acquire()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chatbot_users (id, name) VALUES (%s, %s) "
                    "ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name "
                    "RETURNING *",
                    (user_data.id, user_data.name)
                )
                row = cur.fetchone()
                conn.commit()
                if row:
                    return User(**dict(row))
                return None
        except Exception as e:
            conn.rollback()
            print(f"Error creating user: {e}")
            return None
        finally:
            self._release(conn)

    # ------------------------------------------------------------------ #
    # History  →  chatbot_history
    # ------------------------------------------------------------------ #

    async def get_history(self, user_id: str, minutes: int = 5) -> List[Message]:
        conn = self._acquire()
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=minutes)
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT * FROM chatbot_history "
                    "WHERE user_id = %s AND created_at >= %s "
                    "ORDER BY created_at ASC",
                    (user_id, cutoff)
                )
                rows = cur.fetchall()
                return [Message(**dict(r)) for r in rows]
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
        finally:
            self._release(conn)

    async def add_history(self, message_data: MessageCreate) -> Optional[Message]:
        conn = self._acquire()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO chatbot_history (user_id, content, role, url_imagen) "
                    "VALUES (%s, %s, %s, %s) RETURNING *",
                    (
                        message_data.user_id,
                        message_data.content,
                        message_data.role,
                        message_data.url_imagen,
                    )
                )
                row = cur.fetchone()
                conn.commit()
                if row:
                    return Message(**dict(row))
                return None
        except Exception as e:
            conn.rollback()
            print(f"Error adding message to history: {e}")
            return None
        finally:
            self._release(conn)

    # ------------------------------------------------------------------ #
    # Departamentos  →  propiedades (tabla del sistema existente)
    # ------------------------------------------------------------------ #

    async def get_departments(self, search_query: str) -> List[Department]:
        """Busca propiedades por calle y/o número. search_query puede incluir wildcards (*)."""
        conn = self._acquire()
        try:
            pattern = search_query.replace("*", "%")
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT
                        id::text,
                        TRIM(CONCAT_WS(' ',
                            calle,
                            numero,
                            CASE WHEN piso IS NOT NULL AND piso <> '' THEN 'Piso ' || piso END,
                            CASE WHEN departamento IS NOT NULL AND departamento <> '' THEN 'Dpto ' || departamento END,
                            barrio,
                            localidad
                        )) AS address,
                        created_at
                    FROM propiedades
                    WHERE (deleted IS NULL OR deleted = FALSE)
                      AND (
                            calle ILIKE %s
                         OR CONCAT(calle, ' ', numero) ILIKE %s
                         OR CONCAT(calle, ' ', numero, ' ', COALESCE(piso,''), ' ', COALESCE(departamento,'')) ILIKE %s
                      )
                    LIMIT 50
                    """,
                    (pattern, pattern, pattern)
                )
                rows = cur.fetchall()
                return [Department(**dict(r)) for r in rows]
        except Exception as e:
            print(f"Error searching departments: {e}")
            return []
        finally:
            self._release(conn)

    async def create_department(self, address: str) -> Optional[Department]:
        """Las propiedades se gestionan en el sistema principal, no desde el bot."""
        print(f"create_department: la propiedad '{address}' no existe en el sistema. No se puede crear desde el bot.")
        return None

    async def save_message(
        self,
        departamento_id: str,
        content: str,
        url_imagen: Optional[str] = None
    ) -> bool:
        """Guarda el mensaje en propiedad_actualizaciones usando el UUID del departamento."""
        conn = self._acquire()
        try:
            new_id = str(uuid.uuid4())
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO propiedad_actualizaciones "
                    "(id, propiedad_id, content, url_imagen) "
                    "VALUES (%s, %s::uuid, %s, %s)",
                    (new_id, departamento_id, content, url_imagen)
                )
                conn.commit()
                return True
        except Exception as e:
            conn.rollback()
            print(f"Error saving message to propiedad_actualizaciones: {e}")
            return False
        finally:
            self._release(conn)

    # ------------------------------------------------------------------ #
    # Storage (sin Supabase)
    # ------------------------------------------------------------------ #

    async def upload_image(self, bucket: str, file_path: str, file_data: bytes) -> Optional[str]:
        print("upload_image: almacenamiento de imágenes no configurado")
        return None


# Global instance
supabase_service = SupabaseService()
HEREDOC

# ── models/department.py ──────────────────────────────────────────────────────
cat > models/department.py << 'HEREDOC'
"""
Department models
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DepartmentBase(BaseModel):
    """Base department model"""
    address: str = Field(..., description="Department address")


class DepartmentCreate(DepartmentBase):
    """Model for creating a new department"""
    pass


class Department(DepartmentBase):
    """Department model with ID and timestamps"""
    id: str = Field(..., description="Department UUID")
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
HEREDOC

# ── tools/supabase_tools.py ───────────────────────────────────────────────────
cat > tools/supabase_tools.py << 'HEREDOC'
"""
Supabase tools for Gemini function calling
Tools that the AI agents can use to interact with the database
"""
from google.generativeai.types import FunctionDeclaration, Tool
from services.supabase_client import supabase_service
from typing import Dict, Any, List
import asyncio


# Function declarations for Gemini
buscar_departamento_declaration = FunctionDeclaration(
    name="buscar_departamento",
    description=(
        "Busca una propiedad/departamento en el sistema por dirección (calle y número). "
        "Úsala siempre antes de guardar un mensaje. "
        "Si no se encuentra, informa al usuario que la propiedad no está registrada en el sistema "
        "y que debe cargarla primero desde la aplicación principal."
    ),
    parameters={
        "type": "object",
        "properties": {
            "direccion": {
                "type": "string",
                "description": "Calle y número del departamento. Ej: 'Formosa 380' o 'San Benito de Palermo 1584'"
            }
        },
        "required": ["direccion"]
    }
)

crear_departamento_declaration = FunctionDeclaration(
    name="crear_departamento",
    description=(
        "NO usar — las propiedades se gestionan en el sistema principal, no desde el bot. "
        "Si la propiedad no existe, informar al usuario."
    ),
    parameters={
        "type": "object",
        "properties": {
            "direccion": {"type": "string", "description": "Dirección"}
        },
        "required": ["direccion"]
    }
)

guardar_mensaje_declaration = FunctionDeclaration(
    name="guardar_mensaje",
    description="Úsala para guardar una nota o mensaje sobre un departamento específico. Requiere el ID del departamento y el texto a guardar.",
    parameters={
        "type": "object",
        "properties": {
            "departamento_id": {
                "type": "string",
                "description": "ID (UUID) del departamento (obtenido de buscar_departamento)"
            },
            "contenido": {
                "type": "string",
                "description": "Contenido del mensaje/nota a guardar"
            },
            "url_imagen": {
                "type": "string",
                "description": "URL de la imagen asociada (opcional)"
            }
        },
        "required": ["departamento_id", "contenido"]
    }
)

# Tool object with all Supabase functions
supabase_tool = Tool(
    function_declarations=[
        buscar_departamento_declaration,
        crear_departamento_declaration,
        guardar_mensaje_declaration
    ]
)


# Actual Python functions that execute the tools
def buscar_departamento(direccion: str) -> Dict[str, Any]:
    """Search for departments by address"""
    try:
        search_pattern = f"*{direccion}*"

        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    supabase_service.get_departments(search_pattern)
                )
                departments = future.result()
        else:
            departments = loop.run_until_complete(
                supabase_service.get_departments(search_pattern)
            )

        if not departments:
            return {
                "encontrado": False,
                "mensaje": f"No se encontró ningún departamento con la dirección '{direccion}'",
                "departamentos": []
            }

        return {
            "encontrado": True,
            "cantidad": len(departments),
            "departamentos": [
                {
                    "id": dept.id,
                    "address": dept.address
                }
                for dept in departments
            ]
        }
    except Exception as e:
        return {
            "encontrado": False,
            "error": str(e)
        }


def crear_departamento(direccion: str) -> Dict[str, Any]:
    """No-op: properties managed in main system"""
    return {
        "creado": False,
        "error": "Las propiedades se gestionan en el sistema principal, no desde el bot."
    }


def guardar_mensaje(
    departamento_id: str,
    contenido: str,
    url_imagen: str = None
) -> Dict[str, Any]:
    """Save a message/note about a department"""
    try:
        departamento_id = str(departamento_id).strip()

        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(
                    asyncio.run,
                    supabase_service.save_message(departamento_id, contenido, url_imagen)
                )
                success = future.result()
        else:
            success = loop.run_until_complete(
                supabase_service.save_message(departamento_id, contenido, url_imagen)
            )

        if success:
            return {
                "guardado": True,
                "mensaje": "Mensaje guardado exitosamente",
                "departamento_id": departamento_id
            }
        else:
            return {
                "guardado": False,
                "error": "No se pudo guardar el mensaje"
            }
    except Exception as e:
        return {
            "guardado": False,
            "error": str(e)
        }


# Dictionary mapping function names to actual functions
supabase_tool_functions = {
    "buscar_departamento": buscar_departamento,
    "crear_departamento": crear_departamento,
    "guardar_mensaje": guardar_mensaje
}
HEREDOC

# ── agents/property_agent.py ──────────────────────────────────────────────────
cat > agents/property_agent.py << 'HEREDOC'
"""
Property Management Agent
Handles department management, notes, and search
"""
from .base_agent import BaseAgent
from tools.supabase_tools import supabase_tool, supabase_tool_functions
from typing import Optional, List, Dict


PROPERTY_AGENT_PROMPT = """# SYSTEM PROMPT: AGENTE DE GESTIÓN INMOBILIARIA (WHATSAPP)

**Rol:** Asistente logístico para registrar notas sobre departamentos. Procesás mensajes en lenguaje natural, identificás la propiedad y guardás la información.

## 🛠 FLUJO DE TRABAJO

### PASO 1 — Extraer dirección y nota del mensaje

El usuario puede escribir de muchas formas:
- "en formosa 380 hay una gotera"
- "formosa 380 - gotera en el techo"
- "formosa, hay una gotera"
- "en la formosa hay problema con la llave"

Extraé:
- **Dirección**: la calle (y número si lo menciona). Ej: "formosa", "formosa 380", "san benito de palermo 1584"
- **Nota**: el resto del mensaje. Ej: "hay una gotera", "problema con la llave"

Si el mensaje es ambiguo y no podés separar la dirección de la nota, pedí aclaración antes de seguir.

### PASO 2 — Buscar la propiedad (`buscar_departamento`)

Buscá usando solo la calle (y número si lo tenés). Ejemplos de búsqueda:
- Si dice "formosa 380" → buscá "formosa 380"
- Si dice "en formosa" sin número → buscá "formosa"

**Según el resultado:**

**A) Una sola propiedad encontrada:**
→ Procedé directamente al Paso 3.

**B) Varias propiedades encontradas:**
→ Listálas y preguntale al usuario cuál es. Ejemplo:
"Encontré varias propiedades con ese nombre, ¿cuál es?
1️⃣ Formosa 380, Piso 2 Dpto A - Palermo
2️⃣ Formosa 100 - Belgrano
Respondé con el número."
→ Esperá la respuesta del usuario, luego guardá en la elegida.

**C) Ninguna propiedad encontrada:**
→ Informá: "No encontré ninguna propiedad con esa dirección en el sistema. Tiene que estar cargada en la aplicación principal para poder registrar notas."
→ NO intentés crear la propiedad.

### PASO 3 — Guardar la nota (`guardar_mensaje`)

Usá el ID de la propiedad confirmada y guardá la nota.

### PASO 4 — Confirmar al usuario

Respondé exactamente con este formato:

✅ **Información guardada**
📍 **Depto:** [dirección completa de la propiedad]
💬 **Nota:** [nota registrada]

¿Querés agendar algo en el calendario para este departamento?

## 🧰 HERRAMIENTAS
- `buscar_departamento`: Busca propiedades por dirección (calle y/o número).
- `guardar_mensaje`: Guarda la nota vinculada al ID de la propiedad encontrada."""


class PropertyAgent(BaseAgent):
    """Agent for property/department management"""

    def __init__(self):
        super().__init__(
            name="PropertyAgent",
            system_prompt=PROPERTY_AGENT_PROMPT
        )

    async def handle_message(
        self,
        user_message: str,
        history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[bytes] = None
    ) -> str:
        return await self.process(
            user_message=user_message,
            tools=[supabase_tool],
            tool_functions=supabase_tool_functions,
            history=history,
            image_data=image_data
        )


# Global instance
property_agent = PropertyAgent()
HEREDOC

# ── utils/image_processor.py ──────────────────────────────────────────────────
cat > utils/image_processor.py << 'HEREDOC'
"""
Image processor
Descarga imágenes de WhatsApp para enviar a Gemini.
El almacenamiento en la nube es opcional y no bloquea el flujo.
"""
from services.whatsapp import whatsapp_service
from typing import Optional


async def process_whatsapp_image(
    media_id: str,
    user_id: str,
    bucket_name: str = "fotos_departamentos"
) -> Optional[str]:
    """
    Descarga la imagen de WhatsApp.
    Devuelve None (sin storage externo configurado actualmente).
    Los bytes de la imagen se usan directamente en Gemini via handle_message.
    """
    try:
        print(f"📥 Downloading image {media_id} for Gemini processing...")
        image_data = await whatsapp_service.download_media(media_id)
        if not image_data:
            print("❌ Failed to download image")
        return None
    except Exception as e:
        print(f"❌ Error processing image: {e}")
        return None
HEREDOC

# ── railway_init_db.sql ───────────────────────────────────────────────────────
cat > railway_init_db.sql << 'HEREDOC'
-- Tablas del chatbot WhatsApp
-- Ejecutar una sola vez en Railway: PostgreSQL service → Console → psql $DATABASE_URL

-- Usuarios de WhatsApp
CREATE TABLE IF NOT EXISTS chatbot_users (
  id         TEXT PRIMARY KEY,   -- número WhatsApp (wa_id)
  name       TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Historial de conversación (ventana de 5 minutos)
CREATE TABLE IF NOT EXISTS chatbot_history (
  id         SERIAL PRIMARY KEY,
  user_id    TEXT REFERENCES chatbot_users(id),
  content    TEXT NOT NULL,
  role       TEXT NOT NULL,
  url_imagen TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chatbot_history_user ON chatbot_history(user_id);
CREATE INDEX IF NOT EXISTS idx_chatbot_history_ts   ON chatbot_history(created_at);
HEREDOC

echo ""
echo "✅ Archivos escritos. Commiteando y pusheando a main..."
git add requirements.txt config/settings.py services/supabase_client.py \
        models/department.py tools/supabase_tools.py agents/property_agent.py \
        utils/image_processor.py railway_init_db.sql

git commit -m "fix: migrar a PostgreSQL Railway, agente NLP para propiedades"
git push origin main

echo ""
echo "🚀 Listo! Railway va a re-deployar automáticamente."
echo ""
echo "⚠️  IMPORTANTE: Asegurate de tener en Railway las variables de entorno:"
echo "   DATABASE_URL = postgresql://postgres:ffJWrAxJIJrbgndwcizspHANAJJGHdjI@switchback.proxy.rlwy.net:35870/railway"
echo ""
echo "   Y que hayas corrido el SQL de railway_init_db.sql en la consola de Railway."
