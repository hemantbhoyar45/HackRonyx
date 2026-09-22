from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import dashboard, priority

app = FastAPI(
    title="Water Intelligence API",
    description="Geospatial intelligence platform for satellite-based water quality monitoring",
    version="0.1.0",
)

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development, allow all. Restrict in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(dashboard.router, prefix="/api/dashboard", tags=["dashboard"])
app.include_router(priority.router, prefix="/api/priority", tags=["priority"])

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "Water Intelligence API"}
