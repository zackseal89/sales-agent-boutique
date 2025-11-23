"""
Fashion Boutique WhatsApp AI Sales Agent - Main Application
FastAPI backend for serverless deployment on Google Cloud Run
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from contextlib import asynccontextmanager

# Import routers
from backend.api.webhooks import router as webhooks_router
# from api.dashboard import router as dashboard_router

from dotenv import load_dotenv

load_dotenv()

# Configuration
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    environment: str = "development"
    port: int = 8080
    supabase_url: str
    supabase_service_key: str
    google_api_key: str
    paylink_api_key: str = ""
    paylink_username: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()

# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Fashion Boutique AI Agent API...")
    print(f"Environment: {settings.environment}")
    print(f"Region: africa-south1 (Johannesburg)")
    
    yield
    
    # Shutdown
    print("👋 Shutting down gracefully...")

# Create FastAPI app
app = FastAPI(
    title="Fashion Boutique AI Sales Agent API",
    description="Multi-tenant WhatsApp AI sales agent for fashion boutiques in Kenya",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Health check endpoint (required for Cloud Run)
@app.get("/health")
async def health_check():
    """Health check endpoint for Cloud Run"""
    return {
        "status": "healthy",
        "service": "fashion-boutique-api",
        "environment": settings.environment
    }

# Root endpoint
@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "Fashion Boutique AI Sales Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    print(f"❌ Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

# Include routers
app.include_router(webhooks_router, prefix="/webhooks", tags=["webhooks"])
# Import and include payments router
from backend.api.payments import router as payments_router
app.include_router(payments_router, prefix="/webhooks", tags=["payments"])
# app.include_router(dashboard_router, prefix="/api", tags=["dashboard"])

# Debug endpoint for conversations
@app.get("/debug/conversations")
async def view_all_conversations():
    """Debug endpoint to view active conversation states"""
    try:
        from backend.services.supabase_service import supabase_service
        
        # Query the checkpoints table directly
        response = await supabase_service.client.table("checkpoints").select("thread_id, created_at, metadata").execute()
        
        # Group by thread_id to get unique conversations
        conversations = {}
        for row in response.data:
            thread_id = row['thread_id']
            if thread_id not in conversations:
                conversations[thread_id] = {
                    "thread_id": thread_id,
                    "last_active": row['created_at'],
                    "metadata": row['metadata']
                }
        
        return {
            "total_active_threads": len(conversations),
            "conversations": list(conversations.values())
        }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development"
    )
