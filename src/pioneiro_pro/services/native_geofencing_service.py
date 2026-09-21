from __future__ import annotations

import json
from typing import Any

import flet as ft


class NativeGeofenceError(RuntimeError):
    pass


@ft.control("pioneiro_pro_geofencing")
class NativeGeofencingService(ft.Service):
    """Bridge to native OS geofencing on mobile builds."""

    @staticmethod
    def _check(result: Any) -> Any:
        if isinstance(result, str) and result.startswith("error:"):
            raise NativeGeofenceError(result[6:])
        return result

    async def initialize(self) -> bool:
        result = await self._invoke_method(method_name="initialize")
        return self._check(result) == "true"

    async def request_permissions(self) -> bool:
        result = await self._invoke_method(method_name="request_permissions")
        return self._check(result) == "true"

    async def sync_regions(self, regions: list[dict]) -> dict:
        result = await self._invoke_method(
            method_name="sync_regions",
            arguments={"regions": regions},
        )
        checked = self._check(result)
        return json.loads(checked) if isinstance(checked, str) else dict(checked or {})

    async def clear_regions(self) -> None:
        result = await self._invoke_method(method_name="clear_regions")
        self._check(result)

    async def registered_ids(self) -> list[str]:
        result = await self._invoke_method(method_name="registered_ids")
        checked = self._check(result)
        return list(json.loads(checked)) if isinstance(checked, str) else list(checked or [])

    async def is_background_restricted(self) -> bool:
        result = await self._invoke_method(method_name="is_background_restricted")
        return self._check(result) == "true"

    async def is_ignoring_battery_optimizations(self) -> bool:
        result = await self._invoke_method(
            method_name="is_ignoring_battery_optimizations"
        )
        return self._check(result) == "true"

    async def consume_last_event(self) -> dict | None:
        result = await self._invoke_method(method_name="consume_last_event")
        checked = self._check(result)
        if not checked:
            return None
        data = json.loads(checked)
        return data if isinstance(data, dict) else None
