# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import Base, engine
from app.api.routes import metrics, auth, alerts
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BACKEND] %(levelname)s %(message)s"
)

# Create all PostgreSQL tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Monitoring System API",
    description="Real-time metrics collection and alerting",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])

@app.get("/health")
def health():
    return {"status": "healthy"}