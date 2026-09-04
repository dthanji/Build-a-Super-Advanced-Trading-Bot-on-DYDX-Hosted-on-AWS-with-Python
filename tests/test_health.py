from datetime import datetime, timedelta, timezone

from src.monitoring.health import HealthState


def test_health_requires_fresh_loop_and_market_data():
    health = HealthState()
    assert not health.healthy()
    health.mark_loop()
    health.mark_market_data()
    assert health.healthy()


def test_health_fails_after_error_limit():
    health = HealthState(datetime.now(timezone.utc), datetime.now(timezone.utc))
    health.mark_error(); health.mark_error(); health.mark_error()
    assert not health.healthy()


def test_health_rejects_stale_market_data():
    old = datetime.now(timezone.utc) - timedelta(minutes=10)
    health = HealthState(old, datetime.now(timezone.utc))
    assert not health.healthy()
