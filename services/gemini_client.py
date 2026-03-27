"""
Google Gemini AI client
Handles AI agent calls with function calling (tools)
"""
import google.generativeai as genai
from google.generativeai.types import FunctionDeclaration, Tool, GenerateContentResponse
from config.settings import settings
from typing import List, Dict, Any, Optional, Callable
import json


class GeminiService:
    """Service for interacting with Google Gemini AI"""
    
    def __init__(self):
        genai.configure(api_key=settings.gemini_api_key)
        self.model_name = settings.gemini_model
    
    async def chat_with_tools(
        self,
        system_prompt: str,
        user_message: str,
        tools: List[Tool],
        tool_functions: Dict[str, Callable],
        history: Optional[List[Dict[str, str]]] = None,
        image_data: Optional[bytes] = None,
        mime_type: Optional[str] = "image/jpeg"
    ) -> str:
        """
        Execute a chat with function calling capability
        
        Args:
            system_prompt: System instructions for the AI
            user_message: User's message/query
            tools: List of Tool objects (function declarations)
            tool_functions: Dict mapping function names to actual Python functions
            history: Optional chat history
            image_data: Optional image bytes for vision models
            mime_type: MIME type of the image
            
        Returns:
            AI's final response as string
        """
        try:
            # Create model with tools
            model = genai.GenerativeModel(
                model_name=self.model_name,
                tools=tools,
                system_instruction=system_prompt
            )
            
            # Start chat with history
            chat = model.start_chat(history=history or [])
            
            # Prepare message content
            if image_data:
                # For images, send as multimodal content
                message_content = [
                    user_message,
                    {"mime_type": mime_type, "data": image_data}
                ]
            else:
                message_content = user_message
            
            # Send initial message
            response = chat.send_message(message_content)
            
            # Handle function calling loop
            max_iterations = 5
            iteration = 0
            
            while iteration < max_iterations:
                # Check if model wants to call a function
                if not response.candidates:
                    break
                
                part = response.candidates[0].content.parts[0]
                
                # If we have a text response, we're done
                if hasattr(part, 'text') and part.text:
                    return part.text
                
                # If we have a function call, execute it
                if hasattr(part, 'function_call') and part.function_call:
                    function_call = part.function_call
                    function_name = function_call.name
                    function_args = dict(function_call.args)
                    
                    print(f"🔧 AI calling function: {function_name} with args: {function_args}")
                    
                    # Execute the function
                    if function_name in tool_functions:
                        try:
                            # Call the actual function
                            if asyncio.iscoroutinefunction(tool_functions[function_name]):
                                function_result = await tool_functions[function_name](**function_args)
                            else:
                                function_result = tool_functions[function_name](**function_args)
                            
                            # Convert result to JSON string
                            result_json = json.dumps(function_result, ensure_ascii=False)
                            
                            print(f"✅ Function result: {result_json}")
                            
                            # Send function response back to model
                            response = chat.send_message(
                                genai.protos.Content(parts=[
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response={"result": function_result}
                                        )
                                    )
                                ])
                            )
                        except Exception as e:
                            error_msg = f"Error executing function {function_name}: {str(e)}"
                            print(f"❌ {error_msg}")
                            
                            # Send error back to model
                            response = chat.send_message(
                                genai.protos.Content(parts=[
                                    genai.protos.Part(
                                        function_response=genai.protos.FunctionResponse(
                                            name=function_name,
                                            response={"error": error_msg}
                                        )
                                    )
                                ])
                            )
                    else:
                        print(f"❌ Unknown function: {function_name}")
                        break
                else:
                    # No text and no function call, break
                    break
                
                iteration += 1
            
            # If we exhausted iterations or got no response, return a default message
            if response.candidates and response.candidates[0].content.parts:
                part = response.candidates[0].content.parts[0]
                if hasattr(part, 'text') and part.text:
                    return part.text
            
            return "Lo siento, no pude procesar tu solicitud."
            
        except Exception as e:
            print(f"Error in Gemini chat: {e}")
            return f"Error: {str(e)}"


# Import asyncio for async function check
import asyncio

# Global instance
gemini_service = GeminiService()
