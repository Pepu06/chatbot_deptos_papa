"""
FastAPI WhatsApp Bot - Main Application
Chatbot de WhatsApp con IA para gestión inmobiliaria y calendario
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from routes.webhook import router as webhook_router

app = FastAPI(
    title="WhatsApp Bot API",
    description="Chatbot de WhatsApp con Google Gemini para gestión inmobiliaria",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(webhook_router, prefix="/webhook", tags=["webhook"])

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "WhatsApp Bot API",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    """Detailed health check"""
    return {
        "status": "healthy",
        "timezone": str(settings.TIMEZONE),
        "gemini_model": settings.GEMINI_MODEL
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG
    )
