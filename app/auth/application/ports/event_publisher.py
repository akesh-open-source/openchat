from __future__ import annotations

from typing import Any, Protocol


class EventPublisher(Protocol):
    """Port for publishing application/domain events."""

    async def publish(self, event_name: str, payload: dict[str, Any]) -> None:
        ...
