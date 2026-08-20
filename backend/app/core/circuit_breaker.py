import time
from datetime import datetime, timezone, timedelta
from typing import Tuple, Optional
from app.core.logging import logger

class GoogleCircuitBreaker:
    def __init__(self, threshold: int = 3, cooldown_seconds: int = 1800):
        self.threshold = threshold
        self.cooldown_seconds = cooldown_seconds
        self.consecutive_429s = 0
        self.exhausted_until: Optional[float] = None

    def is_exhausted(self) -> Tuple[bool, Optional[str]]:
        if self.exhausted_until is not None:
            now = time.time()
            if now < self.exhausted_until:
                expiry_dt = datetime.fromtimestamp(self.exhausted_until, tz=timezone.utc)
                return True, expiry_dt.strftime("%H:%M:%S UTC")
            else:
                # Cooldown expired, reset circuit breaker
                logger.info("GoogleCircuitBreaker: Cooldown expired. Resetting Google circuit breaker.")
                self.exhausted_until = None
                self.consecutive_429s = 0
                return False, None
        return False, None

    def record_429(self, service_name: str = "google_places"):
        self.consecutive_429s += 1
        logger.warning(f"GoogleCircuitBreaker [{service_name}]: Received 429 rate limit ({self.consecutive_429s}/{self.threshold}).")
        if self.consecutive_429s >= self.threshold:
            self.exhausted_until = time.time() + self.cooldown_seconds
            expiry_dt = datetime.fromtimestamp(self.exhausted_until, tz=timezone.utc)
            logger.error(f"GoogleCircuitBreaker [{service_name}]: Quota exhausted! Tripping circuit breaker until {expiry_dt.strftime('%H:%M:%S UTC')}.")

    def record_success(self, service_name: str = "google_places"):
        if self.consecutive_429s > 0:
            logger.info(f"GoogleCircuitBreaker [{service_name}]: Call succeeded. Resetting consecutive 429 counter.")
        self.consecutive_429s = 0

google_circuit_breaker = GoogleCircuitBreaker()
