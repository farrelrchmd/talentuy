"""Waktu UTC naive yang konsisten untuk seluruh aplikasi."""

from datetime import datetime, timezone


def utcnow() -> datetime:
    """UTC saat ini tanpa tzinfo, agar cocok dengan kolom DateTime naive."""
    return datetime.now(timezone.utc).replace(tzinfo=None)
