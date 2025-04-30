
from fastapi import FastAPI
from app.routes import messages

app = FastAPI(title="Message Hub Beta")

app.include_router(messages.router, prefix="/api/messages")
