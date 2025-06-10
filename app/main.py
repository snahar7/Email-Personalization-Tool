from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.endpoints import router as api_router
from app.database.database import engine
from app.models.models import Base

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Email Personalization Tool",
    description="API for managing companies and prospects with research information",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to Email Personalization Tool API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"} 