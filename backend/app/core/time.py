from datetime import UTC, datetime


def utcnow() -> datetime:
    return datetime.now(UTC)


def como_utc(momento: datetime | None) -> datetime | None:
    if momento is None or momento.tzinfo is not None:
        return momento
    return momento.replace(tzinfo=UTC)
