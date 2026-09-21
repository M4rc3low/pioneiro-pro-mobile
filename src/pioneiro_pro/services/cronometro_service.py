from __future__ import annotations

import time


class CronometroService:
    def __init__(self) -> None:
        self._acumulado = 0.0
        self._inicio: float | None = None

    @property
    def rodando(self) -> bool:
        return self._inicio is not None

    def iniciar(self) -> None:
        if self._inicio is None:
            self._inicio = time.monotonic()

    def pausar(self) -> None:
        if self._inicio is not None:
            self._acumulado += time.monotonic() - self._inicio
            self._inicio = None

    def zerar(self) -> None:
        self._acumulado = 0.0
        self._inicio = None

    def segundos(self) -> int:
        total = self._acumulado
        if self._inicio is not None:
            total += time.monotonic() - self._inicio
        return max(0, int(total))

    def minutos_para_registro(self) -> int:
        segundos = self.segundos()
        if segundos <= 0:
            return 0
        return max(1, round(segundos / 60))

    def texto(self) -> str:
        total = self.segundos()
        horas, resto = divmod(total, 3600)
        minutos, segundos = divmod(resto, 60)
        return f"{horas:02d}:{minutos:02d}:{segundos:02d}"
