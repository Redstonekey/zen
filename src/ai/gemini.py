import google.generativeai as genai
import asyncio
from typing import Any, List, Optional, Union, AsyncGenerator


class Gemini:
    """Simple Gemini AI client with just the basics."""
    
    def __init__(self, api_key: str, model: str, system_instruction: str = None):
        """
        Initialize the Gemini client.
        
        Args:
            api_key: Gemini API key
            model: Model name to use
            system_instruction: System instruction for the model
        """
        self.api_key = api_key
        self.model_name = model
        self.system_instruction = system_instruction
        
        # Configure the API
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_instruction
        )
        
        self.chat_sessions = {}  # Store multiple chat sessions by name
        self.current_chat = None  # Current active chat session name
    
    def generate(self, prompt: Union[str, List[Any]]) -> str:
        """
        Generate response from prompt.
        
        Args:
            prompt: Text prompt or list of content
            
        Returns:
            Generated response text
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {e}")
    
    async def generate_async(self, prompt: Union[str, List[Any]]) -> str:
        """
        Generate response asynchronously.
        
        Args:
            prompt: Text prompt or list of content
            
        Returns:
            Generated response text
        """
        try:
            response = await self.model.generate_content_async(prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Error generating response: {e}")
    
    def start_chat(self, name: str = "default", history: Optional[List] = None) -> None:
        """
        Start a new chat session.
        
        Args:
            name: Name of the chat session
            history: Optional chat history to continue from
        """
        self.chat_sessions[name] = self.model.start_chat(history=history or [])
        self.current_chat = name
    
    def switch_chat(self, name: str) -> None:
        """Switch to a different chat session."""
        if name in self.chat_sessions:
            self.current_chat = name
        else:
            raise ValueError(f"Chat session '{name}' not found")
    
    def list_chats(self) -> List[str]:
        """List all available chat sessions."""
        return list(self.chat_sessions.keys())
    
    def chat(self, message: Union[str, List[Any]], chat_name: str = None) -> str:
        """
        Send a message in chat session.
        
        Args:
            message: Message to send
            chat_name: Name of chat session (uses current if not specified)
            
        Returns:
            Response text
        """
        chat_name = chat_name or self.current_chat
        
        if not chat_name or chat_name not in self.chat_sessions:
            self.start_chat(chat_name or "default")
            chat_name = chat_name or "default"
        
        try:
            response = self.chat_sessions[chat_name].send_message(message)
            return response.text
        except Exception as e:
            raise Exception(f"Error in chat: {e}")
    
    async def chat_async(self, message: Union[str, List[Any]], chat_name: str = None) -> str:
        """
        Send a message in chat session asynchronously.
        
        Args:
            message: Message to send
            chat_name: Name of chat session (uses current if not specified)
            
        Returns:
            Response text
        """
        chat_name = chat_name or self.current_chat
        
        if not chat_name or chat_name not in self.chat_sessions:
            self.start_chat(chat_name or "default")
            chat_name = chat_name or "default"
        
        try:
            response = await self.chat_sessions[chat_name].send_message_async(message)
            return response.text
        except Exception as e:
            raise Exception(f"Error in chat: {e}")
    
    def get_chat_history(self, chat_name: str = None) -> List:
        """
        Get the chat history for a specific chat session.
        
        Args:
            chat_name: Name of chat session (uses current if not specified)
            
        Returns:
            Chat history
        """
        chat_name = chat_name or self.current_chat
        
        if not chat_name or chat_name not in self.chat_sessions:
            return []
        return self.chat_sessions[chat_name].history
    
    def clear_chat(self, chat_name: str = None) -> None:
        """
        Clear a specific chat session.
        
        Args:
            chat_name: Name of chat session to clear (clears current if not specified)
        """
        chat_name = chat_name or self.current_chat
        
        if chat_name and chat_name in self.chat_sessions:
            del self.chat_sessions[chat_name]
            if self.current_chat == chat_name:
                self.current_chat = None
    
    def clear_all_chats(self) -> None:
        """Clear all chat sessions."""
        self.chat_sessions.clear()
        self.current_chat = None