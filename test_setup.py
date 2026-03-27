"""
Test script to verify configuration and services
Run with: python test_setup.py
"""
import asyncio
from config.settings import settings
from services import supabase_service, whatsapp_service, gemini_service


async def test_config():
    """Test configuration loading"""
    print("🧪 Testing Configuration...")
    print(f"  ✓ Supabase URL: {settings.supabase_url[:30]}...")
    print(f"  ✓ WhatsApp Client ID: {settings.whatsapp_client_id}")
    print(f"  ✓ Gemini Model: {settings.gemini_model}")
    print(f"  ✓ Timezone: {settings.timezone}")
    print()


async def test_supabase():
    """Test Supabase connection"""
    print("🧪 Testing Supabase...")
    try:
        # Try to get a non-existent user (just to test connection)
        user = await supabase_service.get_user("test_user_12345")
        print(f"  ✓ Supabase connection OK (user result: {user is None})")
    except Exception as e:
        print(f"  ✗ Supabase error: {e}")
    print()


async def test_gemini():
    """Test Gemini API"""
    print("🧪 Testing Gemini API...")
    try:
        from tools.supabase_tools import supabase_tool, supabase_tool_functions
        
        response = await gemini_service.chat_with_tools(
            system_prompt="Eres un asistente útil.",
            user_message="Di 'Hola' en una palabra",
            tools=[supabase_tool],
            tool_functions=supabase_tool_functions
        )
        print(f"  ✓ Gemini API OK (response: {response[:50]}...)")
    except Exception as e:
        print(f"  ✗ Gemini error: {e}")
    print()


async def main():
    print("=" * 50)
    print("WhatsApp Bot - Setup Test")
    print("=" * 50)
    print()
    
    await test_config()
    await test_supabase()
    await test_gemini()
    
    print("=" * 50)
    print("✅ Tests completed!")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main())
