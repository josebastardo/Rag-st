from typing import List, Dict
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Message:
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.now)

class ChatSession:
    def __init__(self):
        self.messages: List[Message] = []
        self.context_window: int = 10  # Number of previous messages to keep as context
        
    def add_message(self, role: str, content: str):
        """Add a new message to the chat history."""
        self.messages.append(Message(role=role, content=content))
        
    def get_context(self) -> str:
        """Get the conversation context for the RAG system."""
        recent_messages = self.messages[-self.context_window:] if self.messages else []
        context = "\n".join([
            f"{msg.role}: {msg.content}" 
            for msg in recent_messages
        ])
        return context
    
    def get_messages_for_prompt(self) -> List[Dict[str, str]]:
        """Get messages formatted for the OpenAI API."""
        return [
            {"role": msg.role, "content": msg.content}
            for msg in self.messages[-self.context_window:]
        ]
    
    def clear_history(self):
        """Clear the chat history."""
        self.messages = []
