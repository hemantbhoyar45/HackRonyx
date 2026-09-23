from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import dashboard, priority, analysis, gee, queue, report, validation

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
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(gee.router, prefix="/api/gee", tags=["gee"])
app.include_router(queue.router,   prefix="/api/priority-queue", tags=["priority-queue"])
app.include_router(report.router,      prefix="/api/reports",         tags=["reports"])
app.include_router(validation.router,  prefix="/api/validation",      tags=["validation"])

@app.get("/health")
def health_check():
    return {"status": "operational", "service": "Water Intelligence API"}

