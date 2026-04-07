"""
Supabase client service
Handles all database operations
"""
from supabase import create_client, Client
from config.settings import settings
from models import User, UserCreate, Message, MessageCreate, Department, DepartmentCreate
from typing import List, Optional
from datetime import datetime, timedelta


class SupabaseService:
    """Service for interacting with Supabase database"""
    
    def __init__(self):
        self.client: Client = create_client(
            settings.supabase_url,
            settings.supabase_anon_key
        )
    
    # User operations
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by WhatsApp ID"""
        try:
            response = self.client.table("users").select("*").eq("id", user_id).execute()
            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            return None
        except Exception as e:
            print(f"Error getting user: {e}")
            return None
    
    async def create_user(self, user_data: UserCreate) -> Optional[User]:
        """Create a new user"""
        try:
            # Preparar datos - solo incluir phone si está presente
            user_dict = {
                "id": user_data.id,
                "name": user_data.name,
            }
            
            # Solo agregar phone si está definido y no es None
            if user_data.phone is not None:
                user_dict["phone"] = user_data.phone
            
            response = self.client.table("users").insert(user_dict).execute()
            if response.data and len(response.data) > 0:
                return User(**response.data[0])
            return None
        except Exception as e:
            print(f"Error creating user: {e}")
            # Intentar crear sin el campo phone si falló
            try:
                response = self.client.table("users").insert({
                    "id": user_data.id,
                    "name": user_data.name
                }).execute()
                if response.data and len(response.data) > 0:
                    print(f"✅ User created without phone field")
                    return User(**response.data[0])
            except Exception as e2:
                print(f"Error creating user (retry without phone): {e2}")
            return None
    
    # Message/History operations
    async def get_history(self, user_id: str, minutes: int = 5) -> List[Message]:
        """
        Get message history for user from last N minutes
        Returns messages sorted by created_at ascending (oldest first)
        """
        try:
            cutoff_time = datetime.utcnow() - timedelta(minutes=minutes)
            
            response = self.client.table("history")\
                .select("*")\
                .eq("user_id", user_id)\
                .gte("created_at", cutoff_time.isoformat())\
                .order("created_at", desc=False)\
                .execute()
            
            if response.data:
                return [Message(**msg) for msg in response.data]
            return []
        except Exception as e:
            print(f"Error getting history: {e}")
            return []
    
    async def add_history(self, message_data: MessageCreate) -> Optional[Message]:
        """Add a message to history"""
        try:
            response = self.client.table("history").insert({
                "user_id": message_data.user_id,
                "content": message_data.content,
                "role": message_data.role,
                "url_imagen": message_data.url_imagen
            }).execute()
            
            if response.data and len(response.data) > 0:
                return Message(**response.data[0])
            return None
        except Exception as e:
            print(f"Error adding message to history: {e}")
            return None
    
    # Department operations
    async def get_departments(self, search_query: str) -> List[Department]:
        """
        Search departments by address (case-insensitive, partial match)
        search_query should be wrapped with * for wildcards: *address*
        """
        try:
            # Remove asterisks and use ilike for pattern matching
            pattern = search_query.replace("*", "%")
            
            response = self.client.table("departamentos")\
                .select("*")\
                .ilike("address", pattern)\
                .limit(50)\
                .execute()
            
            if response.data:
                return [Department(**dept) for dept in response.data]
            return []
        except Exception as e:
            print(f"Error searching departments: {e}")
            return []
    
    async def create_department(self, address: str) -> Optional[Department]:
        """Create a new department"""
        try:
            response = self.client.table("departamentos").insert({
                "address": address
            }).execute()
            
            if response.data and len(response.data) > 0:
                return Department(**response.data[0])
            return None
        except Exception as e:
            print(f"Error creating department: {e}")
            return None
    
    async def save_message(
        self,
        departamento_id: int,
        content: str,
        url_imagen: Optional[str] = None
    ) -> bool:
        """Save a message/note about a department"""
        try:
            response = self.client.table("mensajes").insert({
                "departamento_id": departamento_id,
                "content": content,
                "url_imagen": url_imagen
            }).execute()
            
            return response.data is not None and len(response.data) > 0
        except Exception as e:
            print(f"Error saving message: {e}")
            return False
    
    # Storage operations for images
    async def upload_image(self, bucket: str, file_path: str, file_data: bytes) -> Optional[str]:
        """
        Upload image to Supabase storage
        Returns public URL if successful
        """
        try:
            response = self.client.storage.from_(bucket).upload(
                file_path,
                file_data,
                {"content-type": "image/jpeg"}
            )
            
            if response:
                # Get public URL
                public_url = self.client.storage.from_(bucket).get_public_url(file_path)
                return public_url
            return None
        except Exception as e:
            print(f"Error uploading image: {e}")
            return None


# Global instance
supabase_service = SupabaseService()
