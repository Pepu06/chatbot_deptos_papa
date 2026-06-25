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
