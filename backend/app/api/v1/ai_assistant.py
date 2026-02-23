from app.core.config import settings
import httpx
from fastapi import APIRouter, Depends, HTTPException, status
from app.core.database import get_supabase
from app.api.dependencies import get_current_user
from app.schemas.chat import (
    ChatCreate, ChatResponse, MessageCreate, MessageResponse, ChatListResponse, MessageListResponse
)
from app.schemas.auth import UserResponse
from app.schemas.user import UserUpdate
from datetime import datetime
from typing import List

router = APIRouter()

OPENROUTER_MODEL = settings.OPENROUTER_MODEL
OPENROUTER_API_KEY = settings.OPENROUTER_API_KEY
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- Chat Endpoints ---

@router.post("/chats", response_model=ChatResponse)
async def create_chat(
    chat: ChatCreate,
    supabase=Depends(get_supabase),
    current_user=Depends(get_current_user)
):
    data = {
        "user_id": current_user["id"],
        "title": chat.title or "AI Medical Assistant",
        "created_at": datetime.utcnow().isoformat(),
        "last_message_at": datetime.utcnow().isoformat(),
    }
    response = supabase.table("chats").insert(data).execute()
    if not response.data:
        raise HTTPException(status_code=500, detail="Failed to create chat")
    chat_row = response.data[0]
    return ChatResponse(
        id=chat_row["id"],
        title=chat_row.get("title"),
        created_at=chat_row["created_at"],
        last_message_at=chat_row.get("last_message_at"),
    )

@router.get("/chats", response_model=ChatListResponse)
async def list_chats(
    supabase=Depends(get_supabase),
    current_user=Depends(get_current_user)
):
    response = supabase.table("chats").select("*").eq("user_id", current_user["id"]).order("last_message_at", desc=True).execute()
    chats = [
        ChatResponse(
            id=row["id"],
            title=row.get("title"),
            created_at=row["created_at"],
            last_message_at=row.get("last_message_at"),
        ) for row in response.data
    ]
    return ChatListResponse(chats=chats)

@router.delete("/chats/{chat_id}", status_code=204)
async def delete_chat(
    chat_id: str,
    supabase=Depends(get_supabase),
    current_user=Depends(get_current_user)
):
    # Only allow deleting own chats
    chat = supabase.table("chats").select("*").eq("id", chat_id).eq("user_id", current_user["id"]).execute()
    if not chat.data:
        raise HTTPException(status_code=404, detail="Chat not found")
    supabase.table("chats").delete().eq("id", chat_id).execute()
    return

# --- Message Endpoints ---

@router.get("/chats/{chat_id}/messages", response_model=MessageListResponse)
async def get_messages(
    chat_id: str,
    supabase=Depends(get_supabase),
    current_user=Depends(get_current_user)
):
    # Only allow access to own chats
    chat = supabase.table("chats").select("*").eq("id", chat_id).eq("user_id", current_user["id"]).execute()
    if not chat.data:
        raise HTTPException(status_code=404, detail="Chat not found")
    response = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at").execute()
    messages = [
        MessageResponse(
            id=row["id"],
            chat_id=row["chat_id"],
            sender=row["sender"],
            content=row["content"],
            created_at=row["created_at"],
        ) for row in response.data
    ]
    return MessageListResponse(messages=messages)

@router.post("/chats/{chat_id}/messages", response_model=MessageResponse)
async def post_message(
    chat_id: str,
    message: MessageCreate,
    supabase=Depends(get_supabase),
    current_user=Depends(get_current_user)
):
    # Only allow posting to own chats
    chat = supabase.table("chats").select("*").eq("id", chat_id).eq("user_id", current_user["id"]).execute()
    if not chat.data:
        raise HTTPException(status_code=404, detail="Chat not found")
    # Store user message
    msg_data = {
        "chat_id": chat_id,
        "sender": "user",
        "content": message.content,
        "created_at": datetime.utcnow().isoformat(),
    }
    msg_resp = supabase.table("messages").insert(msg_data).execute()
    if not msg_resp.data:
        raise HTTPException(status_code=500, detail="Failed to store message")
    # user_msg = msg_resp.data[0]
    # Fetch user profile for context
    user_profile = supabase.table("profiles").select("*").eq("id", current_user["id"]).single().execute().data
    # Fetch recent chat history (last 10 messages)
    history_resp = supabase.table("messages").select("*").eq("chat_id", chat_id).order("created_at", desc=True).limit(10).execute()
    history = list(reversed(history_resp.data)) if history_resp.data else []
    # Prepare LLM prompt
    prompt = _build_llm_prompt(user_profile, history)
    ai_content = await _call_openrouter_llm(prompt)
    # Store AI message
    ai_msg_data = {
        "chat_id": chat_id,
        "sender": "ai",
        "content": ai_content,
        "created_at": datetime.utcnow().isoformat(),
    }
    ai_msg_resp = supabase.table("messages").insert(ai_msg_data).execute()
    # Update chat last_message_at
    supabase.table("chats").update({"last_message_at": datetime.utcnow().isoformat()}).eq("id", chat_id).execute()
    if not ai_msg_resp.data:
        raise HTTPException(status_code=500, detail="Failed to store AI message")
    ai_msg = ai_msg_resp.data[0]
    return MessageResponse(
        id=ai_msg["id"],
        chat_id=ai_msg["chat_id"],
        sender=ai_msg["sender"],
        content=ai_msg["content"],
        created_at=ai_msg["created_at"]
    )

# --- Helper Functions ---

def _build_llm_prompt(user_profile, history):
    profile_str = f"User Info:\nName: {user_profile.get('name')}\nAge: {user_profile.get('age')}\nGender: {user_profile.get('gender')}\nPhone: {user_profile.get('phone')}\nEmergency Contact: {user_profile.get('emergency_contact')}\n"
    chat_history = "\n".join([
        f"{msg['sender'].capitalize()}: {msg['content']}" for msg in history
    ])
    return f"{profile_str}\nChat History:\n{chat_history}\nUser: {history[-1]['content'] if history else ''}\nAI:"

async def _call_openrouter_llm(prompt: str) -> str:
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": [
            {"role": "system", "content": "You are an AI Medical Assistant. Answer user medical queries in a helpful, safe, and user-specific way."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": 512,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]
