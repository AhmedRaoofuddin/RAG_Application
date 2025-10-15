import logging

from app.api.api_v1.api import api_router
from app.api.openapi.api import router as openapi_router
from app.core.config import settings
from app.core.minio import init_minio
from app.startup.migarate import DatabaseMigrator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:3002"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(openapi_router, prefix="/openapi")


@app.on_event("startup")
async def startup_event():
    import logging
    logger = logging.getLogger(__name__)
    
    # Initialize MinIO
    init_minio()
    
    # Run database migrations
    migrator = DatabaseMigrator(settings.get_database_url)
    migrator.run_migrations()
    
    # Create guest user for development (no-auth mode)
    try:
        from app.db.session import SessionLocal
        from app.models.user import User
        
        db = SessionLocal()
        guest_user = db.query(User).filter(User.username == "guest").first()
        
        if not guest_user:
            # Create guest user with simple password (bcrypt will handle it)
            guest_user = User(
                email="guest@fortes.local",
                username="guest",
                hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYzxHGvz6YC",  # Pre-hashed "guest"
                is_active=True
            )
            db.add(guest_user)
            db.commit()
            logger.info("✅ Guest user created for no-auth mode")
        else:
            logger.info("✅ Guest user already exists")
        
        db.close()
    except Exception as e:
        logger.warning(f"Guest user creation failed (non-critical): {e}")


@app.get("/")
def root():
    return {
        "message": "Welcome to Fortes Eduction API",
        "version": settings.VERSION,
        "project": settings.PROJECT_NAME,
        "features": [
            "RAG Q&A with citations",
            "Guardrails (injection detection, PII redaction, grounding validation)",
            "Attribution & hallucination detection",
            "Observability & cost tracking"
        ]
    }


@app.get("/api/health")
async def health_check():
    import os
    from app.db.session import SessionLocal
    
    # Get absolute DB path
    db_url = settings.get_database_url
    if "sqlite" in db_url:
        # Extract path from sqlite:///path
        db_path = db_url.replace("sqlite:///", "").replace("sqlite://", "")
        if not os.path.isabs(db_path):
            db_path = os.path.abspath(db_path)
    else:
        db_path = db_url
    
    # Test DB connection
    db_status = "ok"
    try:
        from sqlalchemy import text
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
    except Exception as e:
        db_status = f"error: {str(e)}"
    
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "database": {
            "status": db_status,
            "path": db_path,
            "type": "sqlite" if "sqlite" in db_url else "mysql"
        }
    }
