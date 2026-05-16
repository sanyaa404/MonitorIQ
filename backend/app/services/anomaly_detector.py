# backend/app/services/anomaly_detector.py
import logging
import numpy as np
from collections import deque
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from app.schemas.metrics import MetricPayload

log = logging.getLogger(__name__)

WARMUP_POINTS = 200
RETRAIN_EVERY = 100
ANOMALY_THRESHOLD = -0.58
CONTAMINATION = 0.01


class AnomalyDetector:
    def __init__(self, hostname: str):
        self.hostname = hostname
        self.model = None
        self.scaler = StandardScaler()
        self.buffer = deque(maxlen=500)
        self.points_since_retrain = 0
        self.is_trained = False
        self.total_points = 0
        self.anomaly_count = 0

    def _extract_features(self, payload: MetricPayload) -> list:
        return [
            payload.cpu.cpu_percent_total,
            payload.cpu.load_avg_1m,
            payload.cpu.load_avg_5m,
            payload.memory.ram_percent,
            payload.memory.swap_percent,
            payload.processes.total_processes,
        ]

    def _train(self):
        if len(self.buffer) < WARMUP_POINTS:
            return
        X = np.array(list(self.buffer))
        try:
            self.scaler = StandardScaler()
            X_scaled = self.scaler.fit_transform(X)
            self.model = IsolationForest(
                n_estimators=100,
                contamination=CONTAMINATION,
                random_state=42,
                n_jobs=-1,
            )
            self.model.fit(X_scaled)
            self.is_trained = True
            self.points_since_retrain = 0
            log.info(f"[ML] Model trained on {len(self.buffer)} points for host={self.hostname}")
        except Exception as e:
            log.error(f"[ML] Training failed: {e}")

    def _zscore_check(self, features: list) -> bool:
        if len(self.buffer) < 30:
            return False
        arr = np.array(list(self.buffer))
        means = arr.mean(axis=0)
        stds = arr.std(axis=0)
        stds[stds == 0] = 1
        zscores = np.abs((np.array(features) - means) / stds)
        return bool(np.any(zscores > 3.0))

    def process(self, payload: MetricPayload) -> dict:
        features = self._extract_features(payload)
        self.buffer.append(features)
        self.total_points += 1
        self.points_since_retrain += 1

        if self.total_points < WARMUP_POINTS:
            remaining = WARMUP_POINTS - self.total_points
            log.info(f"[ML] Warming up — {remaining} points remaining")
            return {
                "is_anomaly": False,
                "score": None,
                "status": "warming_up",
                "points_collected": self.total_points,
                "warmup_required": WARMUP_POINTS,
            }

        if not self.is_trained or self.points_since_retrain >= RETRAIN_EVERY:
            self._train()

        if not self.is_trained:
            return {"is_anomaly": False, "score": None, "status": "training"}

        try:
            X = np.array([features])
            X_scaled = self.scaler.transform(X)
            score = float(self.model.score_samples(X_scaled)[0])

            isolation_anomaly = score < ANOMALY_THRESHOLD
            zscore_anomaly = self._zscore_check(features)
            is_anomaly = isolation_anomaly and zscore_anomaly

            if is_anomaly:
                self.anomaly_count += 1
                log.warning(
                    f"[ML] ANOMALY DETECTED | host={self.hostname} | "
                    f"score={score:.4f} | "
                    f"CPU={features[0]:.1f}% | "
                    f"RAM={features[3]:.1f}%"
                )

            return {
                "is_anomaly": is_anomaly,
                "score": round(score, 4),
                "status": "active",
                "features": {
                    "cpu_percent": features[0],
                    "load_avg_1m": features[1],
                    "load_avg_5m": features[2],
                    "ram_percent": features[3],
                    "swap_percent": features[4],
                    "total_processes": features[5],
                },
                "total_points": self.total_points,
                "anomaly_count": self.anomaly_count,
            }

        except Exception as e:
            log.error(f"[ML] Scoring failed: {e}")
            return {"is_anomaly": False, "score": None, "status": "error"}


_detectors: dict[str, AnomalyDetector] = {}


def get_detector(hostname: str) -> AnomalyDetector:
    if hostname not in _detectors:
        _detectors[hostname] = AnomalyDetector(hostname)
        log.info(f"[ML] Created new detector for host={hostname}")
    return _detectors[hostname]


def run_anomaly_detection(payload: MetricPayload) -> dict:
    detector = get_detector(payload.hostname)
    return detector.process(payload)