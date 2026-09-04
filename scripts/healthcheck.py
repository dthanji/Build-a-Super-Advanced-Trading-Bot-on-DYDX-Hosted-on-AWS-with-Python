"""Minimal deployment health check; does not access or mutate trading accounts."""
from src.monitoring.health import HealthState


if __name__ == "__main__":
    state = HealthState()
    state.mark_loop()
    state.mark_market_data()
    raise SystemExit(0 if state.healthy() else 1)
