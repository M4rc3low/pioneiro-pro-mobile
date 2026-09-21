from __future__ import annotations

import math
from datetime import datetime, timedelta

from pioneiro_pro.repositories import EstudanteRepository, VisitaRepository


class ProximidadeService:
    def __init__(
        self,
        estudantes: EstudanteRepository,
        visitas: VisitaRepository,
    ) -> None:
        self.estudantes = estudantes
        self.visitas = visitas
        self._ultimos_alertas: dict[str, datetime] = {}

    @staticmethod
    def url_google_maps(latitude: float, longitude: float) -> str:
        lat = f"{float(latitude):.7f}"
        lon = f"{float(longitude):.7f}"
        return (
            "https://www.google.com/maps/dir/?api=1"
            f"&destination={lat}%2C{lon}"
            "&travelmode=driving"
            "&dir_action=navigate"
        )

    @staticmethod
    def distancia_metros(
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float,
    ) -> float:
        raio_terra = 6_371_000
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)

        a = (
            math.sin(delta_phi / 2) ** 2
            + math.cos(phi1)
            * math.cos(phi2)
            * math.sin(delta_lambda / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return raio_terra * c

    def _pode_alertar(self, chave: str, agora: datetime) -> bool:
        ultimo = self._ultimos_alertas.get(chave)
        return ultimo is None or agora - ultimo >= timedelta(hours=2)

    def verificar(
        self,
        latitude: float,
        longitude: float,
        agora: datetime | None = None,
    ) -> list[dict]:
        agora = agora or datetime.now()
        encontrados: list[dict] = []
        vistos_estudantes: set[int] = set()

        for visita in self.visitas.listar_para_proximidade():
            distancia = self.distancia_metros(
                latitude,
                longitude,
                float(visita["latitude"]),
                float(visita["longitude"]),
            )
            raio = int(visita.get("raio_alerta_m") or 200)

            if distancia <= raio:
                chave = f'visita:{visita["id"]}'
                if self._pode_alertar(chave, agora):
                    nome = visita.get("estudante_nome") or "revisita"
                    encontrados.append(
                        {
                            "chave": chave,
                            "tipo": "revisita",
                            "titulo": "Revisita próxima",
                            "nome": nome,
                            "distancia_m": int(round(distancia)),
                            "visita_id": visita["id"],
                            "estudante_id": visita.get("estudante_id"),
                            "latitude": float(visita["latitude"]),
                            "longitude": float(visita["longitude"]),
                        }
                    )
                    self._ultimos_alertas[chave] = agora

                if visita.get("estudante_id") is not None:
                    vistos_estudantes.add(int(visita["estudante_id"]))

        for estudante in self.estudantes.listar_com_localizacao():
            estudante_id = int(estudante["id"])
            if estudante_id in vistos_estudantes:
                continue

            distancia = self.distancia_metros(
                latitude,
                longitude,
                float(estudante["latitude"]),
                float(estudante["longitude"]),
            )
            raio = int(estudante.get("raio_alerta_m") or 200)

            if distancia <= raio:
                chave = f"estudante:{estudante_id}"
                if self._pode_alertar(chave, agora):
                    encontrados.append(
                        {
                            "chave": chave,
                            "tipo": "estudante",
                            "titulo": "Estudante próximo",
                            "nome": estudante["nome"],
                            "distancia_m": int(round(distancia)),
                            "estudante_id": estudante_id,
                            "latitude": float(estudante["latitude"]),
                            "longitude": float(estudante["longitude"]),
                        }
                    )
                    self._ultimos_alertas[chave] = agora

        return encontrados
