from __future__ import annotations

from importlib import import_module


class AndroidNotificationService:
    """Best-effort native notifications for Android.

    The dependency is installed only in Android builds. Other platforms
    transparently fall back to the in-app notification experience.
    """

    def __init__(self, page) -> None:
        self.page = page
        self._service = None

        platform_name = str(getattr(page, "platform", "")).lower()
        if "android" not in platform_name:
            return

        try:
            module = import_module("flet_android_notifications")
            service_class = getattr(module, "FletAndroidNotifications")
            self._service = service_class()
        except (ImportError, AttributeError, RuntimeError):
            self._service = None

    @property
    def available(self) -> bool:
        return self._service is not None

    @staticmethod
    def notification_id(item: dict) -> int:
        if item.get("tipo") == "revisita":
            raw_id = int(item.get("visita_id") or 1)
            return 20_000 + (raw_id % 9_000)

        raw_id = int(item.get("estudante_id") or 1)
        return 10_000 + (raw_id % 9_000)

    async def show_proximity(self, item: dict) -> bool:
        if self._service is None:
            return False

        try:
            enabled = await self._service.are_notifications_enabled()
            if not enabled:
                enabled = await self._service.request_permissions()

            if not enabled:
                return False

            distancia = int(item.get("distancia_m") or 0)
            nome = str(item.get("nome") or "Contato")
            titulo = str(item.get("titulo") or "Pioneiro Pro")
            corpo = f"{nome} está a aproximadamente {distancia} m."

            await self._service.show_notification(
                notification_id=self.notification_id(item),
                title=titulo,
                body=corpo,
            )
            return True
        except (RuntimeError, AttributeError, TypeError):
            return False
