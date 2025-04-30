
from fastapi import APIRouter
from pydantic import BaseModel
from datetime import datetime
from typing import List
from app.utils.storage import store_message, get_messages_by_channel

router = APIRouter()

class Message(BaseModel):
    timestamp: str
    from_agent: str
    to_agents: List[str]
    channel: str
    message: str

@router.post("/")
def post_message(msg: Message):
    store_message(msg.dict())
    return {"status": "Message stored", "channel": msg.channel}

@router.get("/channel/{channel_name}")
def get_channel_messages(channel_name: str):
    return get_messages_by_channel(channel_name)
