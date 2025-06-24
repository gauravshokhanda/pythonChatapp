from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.websocket.websocket_server import websocket_app

from app.routes import (
    user_routes,
    chat_routes,
    conversation_routes,
    message_routes
)
app = FastAPI(
    title="Real-Time Chat API",
    docs_url="/api-docs",       # 👈 this replaces /docs
    redoc_url="/api-redoc",     # 👈 this replaces /redoc
    openapi_url="/openapi.json" # 👈 default OpenAPI schema
)


# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket mount
websocket_app(app)  # Mount the Socket.IO or custom WebSocket logic

# Register API routes with tags
@app.get("/")
def read_root():
    return {"status": "Backend is working fine ✅"}

app.include_router(user_routes, tags=["Users"])
app.include_router(chat_routes, tags=["Chat"])
app.include_router(conversation_routes, tags=["Conversations"])
app.include_router(message_routes, tags=["Messages"])
