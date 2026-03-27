"""
Base agent class
"""
from services.gemini_client import gemini_service
from typing import List, Dict, Any, Optional


class BaseAgent:
    """Base class for AI agents"""
    
    def __init__(self, name: str, system_prompt: str):
        self.name = name
        self.system_prompt = system_prompt
        self.gemini = gemini_service
    
    async def process(
        self,
        user_message: str,
        tools: List[Any],
        tool_functions: Dict[str, Any],
        history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[bytes] = None
    ) -> str:
        """
        Process a message with the agent
        
        Args:
            user_message: The user's message
            tools: List of tools available to the agent
            tool_functions: Dictionary of tool functions
            history: Chat history
            image_data: Optional image bytes
            
        Returns:
            Agent's response
        """
        return await self.gemini.chat_with_tools(
            system_prompt=self.system_prompt,
            user_message=user_message,
            tools=tools,
            tool_functions=tool_functions,
            history=history,
            image_data=image_data
        )
