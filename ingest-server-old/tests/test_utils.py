import pytest
from datetime import datetime, timezone
from app.utils import parse_timestamp

def test_valid_iso_z():
    ts = "2025-06-24T21:01:00Z"
    dt = parse_timestamp(ts)
    assert dt == datetime(2025, 6, 24, 21, 1, 0, tzinfo=timezone.utc)

def test_valid_iso_offset():
    ts = "2025-06-24T21:01:00+00:00"
    dt = parse_timestamp(ts)
    assert dt == datetime(2025, 6, 24, 21, 1, 0, tzinfo=timezone.utc)

def test_invalid_format_raises():
    with pytest.raises(ValueError):
        parse_timestamp("invalid-date")
