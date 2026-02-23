from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class ChatCreate(BaseModel):
    title: Optional[str] = None

class ChatResponse(BaseModel):
    id: str
    title: Optional[str]
    created_at: datetime
    last_message_at: Optional[datetime]

class MessageCreate(BaseModel):
    chat_id: str
    content: str
    sender: str = Field(..., pattern='^(user|ai)$')

class MessageResponse(BaseModel):
    id: str
    chat_id: str
    sender: str
    content: str
    created_at: datetime

class ChatListResponse(BaseModel):
    chats: List[ChatResponse]

class MessageListResponse(BaseModel):
    messages: List[MessageResponse]
