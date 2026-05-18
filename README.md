<div align="center">

# MonitorIQ

### Real-time Infrastructure Monitoring with ML Anomaly Detection

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-009688?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)
![Kafka](https://img.shields.io/badge/Apache_Kafka-7.5-231F20?logo=apachekafka)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker)

A production-grade observability platform that collects real-time system metrics, streams them through Apache Kafka, detects anomalies using ML (Isolation Forest + Z-score), and pushes live updates to a React dashboard via WebSockets.

**One command to run the entire system:**
```bash
docker compose up --build
```

</div>

---

## 📸 Screenshots

> Dashboard showing live CPU, memory, network metrics with ML anomaly detection panel

*(Add your screenshot here)*

---

## 🏗️ Architecture

```
┌─────────────────┐     Kafka Produce      ┌──────────────────────┐
│  Python Agent   │ ──────────────────────► │   Apache Kafka       │
│  (psutil)       │                         │   metrics topic      │
│  Every 5s       │                         │   3 partitions       │
└─────────────────┘                         └──────────┬───────────┘
                                                        │ Consumer Thread
                                                        ▼
                                            ┌──────────────────────┐
                                            │   FastAPI Backend    │
                                            │                      │
                                            │  ┌────────────────┐  │
                                            │  │ InfluxDB Write │  │
                                            │  ├────────────────┤  │
                                            │  │ Alert Checker  │  │
                                            │  ├────────────────┤  │
                                            │  │ ML Detector    │  │
                                            │  ├────────────────┤  │
                                            │  │ WS Broadcast   │  │
                                            │  └────────────────┘  │
                                            └──────────────────────┘
                                                 │           │
                                    ┌────────────┘           └────────────┐
                                    ▼                                      ▼
                           ┌─────────────────┐                  ┌─────────────────┐
                           │    InfluxDB      │                  │   PostgreSQL    │
                           │  Time-series    │                  │  Users, Rules   │
                           │  metrics store  │                  │  Alert events   │
                           └─────────────────┘                  └─────────────────┘
                                                                          
                                    WebSocket Push (100ms latency)
                                            │
                                            ▼
                           ┌─────────────────────────────┐
                           │      React Dashboard        │
                           │  Live charts · Anomaly UI   │
                           │  Alerts · Process table     │
                           └─────────────────────────────┘
```

---

## ✨ Features

### Real-time Metrics Collection
- CPU usage (total + per-core), load averages, frequency
- Memory (RAM + swap) with available vs used distinction
- Disk I/O per partition with read/write counters
- Network traffic (bytes sent/received, packet counts)
- Top 10 processes by CPU with status tracking
- Platform-aware collection (macOS + Linux)

### Streaming Pipeline
- **Apache Kafka** with 3-partition `metrics` topic
- Hostname-keyed messages guarantee per-machine ordering
- Automatic HTTP fallback if Kafka is unreachable (graceful degradation)
- Consumer group with auto-offset commit and reconnection

### ML Anomaly Detection
- **Isolation Forest** (scikit-learn) trained on rolling 500-point window
- **Z-score pre-filter** — both must agree before flagging (reduces false positives)
- 200-point warmup period before predictions begin
- Automatic retraining every 100 new points (adapts to system changes)
- Per-host detector registry — each machine gets its own model
- Severity scoring: MEDIUM / HIGH / CRITICAL based on anomaly score

### Intelligent Alerting
- Threshold-based rules (CPU > X%, RAM > Y%) stored in PostgreSQL
- ML-based anomaly alerts from Isolation Forest
- **Email notifications** via Gmail SMTP with HTML templates
- **Cooldown system** — 5-minute suppression prevents alert storms
- Alert acknowledgement workflow in the UI

### Real-time Dashboard
- WebSocket push — metrics appear within ~100ms of collection
- Auto-reconnecting WebSocket with 3-second retry
- Rolling 60-point history for all charts (5 minutes of data)
- Dynamic hostname discovery — no hardcoding required
- Dark mode UI built with React + Tailwind CSS + Recharts

### Infrastructure
- Full **Docker Compose** deployment — one command starts everything
- Health checks with proper dependency ordering
- Automatic service restart on failure
- JWT authentication with bcrypt password hashing
- CORS configured for both development and production

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Metrics Agent | Python 3.12, psutil |
| Message Queue | Apache Kafka (Confluent 7.5) |
| Backend API | FastAPI, Uvicorn |
| Time-series DB | InfluxDB 2.7 |
| Relational DB | PostgreSQL 16 |
| ML / Anomaly | scikit-learn (Isolation Forest), NumPy |
| Cache / Broker | Zookeeper |
| Frontend | React 18, Tailwind CSS, Recharts |
| Real-time | WebSockets (native browser API) |
| Containerization | Docker, Docker Compose |
| Auth | JWT (python-jose), bcrypt (passlib) |

---

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed and running
- Git

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/monitoring-system.git
cd monitoring-system
```

### 2. Configure environment
```bash
cp .env.docker.example .env.docker
```

Edit `.env.docker` with your values (defaults work for local development).

For email notifications, add your Gmail credentials:
```
EMAIL_ENABLED=true
EMAIL_FROM=your@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_TO=alerts@gmail.com
```

### 3. Start the entire system
```bash
docker compose up --build
```

First build takes 3-5 minutes. Subsequent starts take ~30 seconds.

### 4. Access the dashboard
```
http://localhost:80
```

The ML model begins warming up immediately. After ~17 minutes (200 data points) anomaly detection activates automatically.

---

## 📁 Project Structure

```
monitoring-system/
├── agent/                      # Metrics collection agent
│   ├── collectors/             # Individual metric collectors
│   │   ├── cpu.py              # CPU metrics via psutil
│   │   ├── memory.py           # RAM + swap metrics
│   │   ├── disk.py             # Disk usage + I/O
│   │   ├── network.py          # Network traffic (platform-aware)
│   │   └── process.py          # Top processes by CPU
│   ├── producer.py             # Kafka producer with HTTP fallback
│   ├── config.py               # Environment configuration
│   ├── main.py                 # Collection loop (every 5s)
│   ├── Dockerfile
│   └── requirements.txt
│
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/routes/         # HTTP + WebSocket endpoints
│   │   │   ├── metrics.py      # Ingest + query + hosts
│   │   │   ├── alerts.py       # Rules + events CRUD
│   │   │   ├── auth.py         # Register + login
│   │   │   └── ws.py           # WebSocket endpoint
│   │   ├── core/               # Config, DB, security
│   │   │   ├── config.py       # Pydantic settings
│   │   │   ├── database.py     # SQLAlchemy + session
│   │   │   ├── influx.py       # InfluxDB client
│   │   │   └── security.py     # JWT + bcrypt
│   │   ├── models/             # SQLAlchemy ORM models
│   │   ├── schemas/            # Pydantic validation schemas
│   │   └── services/           # Business logic
│   │       ├── kafka_consumer.py   # Kafka consumer thread
│   │       ├── metrics_service.py  # InfluxDB read/write
│   │       ├── alert_service.py    # Threshold alert checker
│   │       ├── anomaly_detector.py # Isolation Forest ML
│   │       ├── notifier.py         # Email notifications
│   │       └── ws_manager.py       # WebSocket connection manager
│   ├── main.py                 # FastAPI app + lifespan
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # React dashboard
│   ├── src/
│   │   ├── components/
│   │   │   ├── charts/         # CpuChart, MemoryChart, NetworkChart
│   │   │   ├── layout/         # Sidebar, Header
│   │   │   └── widgets/        # StatCard, AlertsPanel, AnomalyPanel, ProcessTable
│   │   ├── hooks/
│   │   │   ├── useWebSocket.js # WS connection + rolling history
│   │   │   └── useMetrics.js   # InfluxDB polling hook
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx   # Main monitoring view
│   │   │   └── Alerts.jsx      # Alert rules + events
│   │   └── services/
│   │       └── api.js          # Axios API client
│   ├── nginx.conf              # Production nginx config
│   ├── Dockerfile              # Multi-stage build
│   └── package.json
│
├── postgres/
│   └── init.sql                # DB initialization
├── docker-compose.yml          # Full stack orchestration
├── .env.docker.example         # Environment template
└── README.md
```

---

## 🔌 API Reference

### Metrics
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/metrics/ingest` | Ingest metric payload |
| GET | `/api/v1/metrics/query/{measurement}` | Query time-series data |
| GET | `/api/v1/metrics/hosts` | List known hostnames |
| GET | `/api/v1/metrics/anomaly/status` | ML detector status |

### Alerts
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/alerts/rules` | Create alert rule |
| GET | `/api/v1/alerts/rules` | List active rules |
| GET | `/api/v1/alerts/events` | Recent alert events |
| PATCH | `/api/v1/alerts/events/{id}/acknowledge` | Acknowledge event |

### Auth
| Method | Endpoint | Description |
|---|---|---|
| POST | `/api/v1/auth/register` | Register user |
| POST | `/api/v1/auth/login` | Login, get JWT |

### WebSocket
| Endpoint | Description |
|---|---|
| `ws://host/ws/metrics` | Real-time metric stream |

Full interactive docs: `http://localhost:8000/docs`

---

## 🧠 ML Anomaly Detection

The system uses a two-layer anomaly detection approach:

**Layer 1 — Isolation Forest**
Builds a model of normal system behaviour using 6 features: CPU%, load avg (1m + 5m), RAM%, swap%, and process count. Points that require few random cuts to isolate are flagged as anomalous.

**Layer 2 — Z-score pre-filter**
Before flagging, checks if any feature deviates more than 3 standard deviations from the recent mean. Both layers must agree.

**Scoring**
- Score > -0.5: Normal
- Score < -0.6: Anomaly (MEDIUM)
- Score < -0.7: Anomaly (HIGH/CRITICAL)

**Lifecycle**
```
Warmup (200 pts) → Train → Score → Retrain every 100 pts → ...
```

---

## 🔧 Development

### Run without Docker

**Start infrastructure:**
```bash
docker compose up postgres influxdb kafka zookeeper -d
```

**Backend:**
```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Agent:**
```bash
cd agent
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python3 main.py
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
# http://localhost:5173
```

---

## 📊 Key Design Decisions

**Why Kafka over direct HTTP?**
Decouples producers from consumers. Agents can publish even if the backend is down. Messages persist and are processed when the backend recovers. Enables multiple consumers (backend + future ML service) reading the same stream independently.

**Why InfluxDB + PostgreSQL?**
InfluxDB is optimised for time-ordered data with fast range aggregations. PostgreSQL handles relational data (users, alert rules, events) with proper constraints and relationships. Right tool for each job.

**Why Isolation Forest over thresholds?**
Threshold alerts require manual tuning per environment and miss gradual degradation. Isolation Forest learns what "normal" looks like for each specific machine and flags deviations — catching subtle anomalies and reducing false positives on high-baseline systems.

**Why WebSockets over polling?**
Polling introduces 5-10 second latency and constant HTTP overhead. WebSocket push delivers metrics within ~100ms of collection with a single persistent connection.

---

## 📝 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">
Built with ❤️ — Agent · Kafka · FastAPI · InfluxDB · scikit-learn · React
</div>
