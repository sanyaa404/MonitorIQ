# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import logging

from app.core.database import Base, engine
from app.api.routes import metrics, auth, alerts
from app.api.routes import ws
from app.services.kafka_consumer import start_consumer, set_event_loop

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [BACKEND] %(levelname)s %(message)s"
)

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Pass the running event loop to the consumer thread
    # so it can schedule async WebSocket broadcasts
    loop = asyncio.get_event_loop()
    set_event_loop(loop)
    start_consumer()
    yield


app = FastAPI(
    title="Monitoring System API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost",       # Docker nginx
        "http://localhost:80",    # Docker nginx explicit port
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics.router, prefix="/api/v1/metrics", tags=["Metrics"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(alerts.router, prefix="/api/v1/alerts", tags=["Alerts"])
app.include_router(ws.router, tags=["WebSocket"])


@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}