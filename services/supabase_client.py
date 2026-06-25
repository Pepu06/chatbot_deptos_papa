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
