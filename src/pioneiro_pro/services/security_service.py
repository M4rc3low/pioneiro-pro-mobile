from __future__ import annotations

import flet_local_auth as fla


class LocalSecurityService:
    """Device-backed authentication using biometrics or device credentials."""

    def __init__(self) -> None:
        self._auth = fla.LocalAuthentication()

    async def is_supported(self) -> bool:
        try:
            return bool(await self._auth.is_device_supported())
        except Exception:
            return False

    async def authenticate(self, reason: str) -> bool:
        try:
            return bool(
                await self._auth.authenticate(
                    reason,
                    biometric_only=False,
                    sensitive_transaction=True,
                    persist_across_backgrounding=True,
                )
            )
        except Exception:
            return False
