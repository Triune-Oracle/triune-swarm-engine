
import json
import os

STORAGE_PATH = "message_log.json"

def store_message(message: dict):
    if not os.path.exists(STORAGE_PATH):
        with open(STORAGE_PATH, "w") as f:
            json.dump([], f)
    with open(STORAGE_PATH, "r") as f:
        messages = json.load(f)
    messages.append(message)
    with open(STORAGE_PATH, "w") as f:
        json.dump(messages, f, indent=2)

def get_messages_by_channel(channel: str):
    if not os.path.exists(STORAGE_PATH):
        return []
    with open(STORAGE_PATH, "r") as f:
        messages = json.load(f)
    return [m for m in messages if m["channel"] == channel]
