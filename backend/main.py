# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import Base, engine
from app.api.routes import metrics, auth, alerts
from app.services.kafka_consumer import start_consumer
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BACKEND] %(levelname)s %(message)s"
)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    start_consumer()
    yield
    # Shutdown (nothing to clean up for now)


app = FastAPI(
    title="Monitoring System API",
    description="Real-time metrics collection and alerting",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])


@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}