from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class LocationAccessResult:
    ok: bool
    code: str
    permission: str = ""
    position: Any | None = None

    @property
    def background_granted(self) -> bool:
        return self.permission == "always"


def normalize_permission_status(status: object) -> str:
    """Normalize Flet/geolocator permission enums across package versions."""
    raw = getattr(status, "name", None) or getattr(status, "value", None) or str(status)
    value = str(raw).strip().lower()
    value = value.rsplit(".", 1)[-1]
    value = value.replace("-", "_").replace(" ", "_")

    aliases = {
        "whileinuse": "while_in_use",
        "deniedforever": "denied_forever",
        "unabletodetermine": "unable_to_determine",
    }
    return aliases.get(value, value)


def foreground_location_granted(status: object) -> bool:
    return normalize_permission_status(status) in {"always", "while_in_use"}


def background_location_granted(status: object) -> bool:
    return normalize_permission_status(status) == "always"


async def get_current_position_with_permission(geolocator) -> LocationAccessResult:
    """Validate service + runtime permission before requesting a GPS fix."""
    try:
        if not await geolocator.is_location_service_enabled():
            return LocationAccessResult(False, "service_disabled")

        status = await geolocator.get_permission_status()
        if not foreground_location_granted(status):
            status = await geolocator.request_permission()

        permission = normalize_permission_status(status)
        if not foreground_location_granted(status):
            code = (
                "permission_permanently_denied"
                if permission in {"denied_forever", "permanently_denied"}
                else "permission_denied"
            )
            return LocationAccessResult(False, code, permission=permission)

        position = await geolocator.get_current_position()
        return LocationAccessResult(
            True,
            "ok",
            permission=permission,
            position=position,
        )
    except RuntimeError as exc:
        return LocationAccessResult(False, "runtime_error", permission=str(exc))
