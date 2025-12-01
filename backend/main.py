from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import auth, chat, emails
from app.config import get_settings

settings = get_settings()

app = FastAPI(
    title="AI Email Assistant API",
    description="Backend API for AI-powered email assistant with Gmail integration",
    version="1.0.0"
)

# CORS configuration
allowed_origins = [
    settings.frontend_url,
    "http://localhost:5173",
    "http://localhost:3000",
]

if settings.environment == "production":
    # Add production frontend URL
    allowed_origins = [settings.frontend_url]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(emails.router)

@app.get("/")
async def root():
    return {
        "message": "AI Email Assistant API",
        "status": "running",
        "version": "1.0.0"
    }

@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    print(f"🚀 AI Email Assistant API starting in {settings.environment} mode")
    print(f"📧 Gmail scopes configured: {len(settings.gmail_scopes)} scopes")


@app.on_event("shutdown")
async def shutdown_event():
    print("👋 AI Email Assistant API shutting down")
