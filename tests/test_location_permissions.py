import asyncio

from pioneiro_pro.database import Database
from pioneiro_pro.repositories import ConfiguracaoRepository
from pioneiro_pro.services import (
    background_location_granted,
    foreground_location_granted,
    get_current_position_with_permission,
    normalize_permission_status,
)


class DummyStatus:
    def __init__(self, name: str):
        self.name = name


class DummyPosition:
    latitude = -23.588
    longitude = -46.681


class DummyGeolocator:
    def __init__(self, enabled=True, current="DENIED", requested="WHILE_IN_USE"):
        self.enabled = enabled
        self.current = DummyStatus(current)
        self.requested = DummyStatus(requested)
        self.requested_count = 0

    async def is_location_service_enabled(self):
        return self.enabled

    async def get_permission_status(self):
        return self.current

    async def request_permission(self):
        self.requested_count += 1
        return self.requested

    async def get_current_position(self):
        return DummyPosition()


def test_normaliza_status_de_permissao():
    assert normalize_permission_status(DummyStatus("WHILE_IN_USE")) == "while_in_use"
    assert normalize_permission_status(DummyStatus("DENIED_FOREVER")) == "denied_forever"
    assert normalize_permission_status("GeolocatorPermissionStatus.ALWAYS") == "always"


def test_diferencia_permissao_de_primeiro_e_segundo_plano():
    assert foreground_location_granted(DummyStatus("WHILE_IN_USE"))
    assert foreground_location_granted(DummyStatus("ALWAYS"))
    assert not background_location_granted(DummyStatus("WHILE_IN_USE"))
    assert background_location_granted(DummyStatus("ALWAYS"))


def test_proximidade_nova_instalacao_comeca_desativada(tmp_path):
    db = Database(tmp_path / "config.db")
    db.initialize()
    config = ConfiguracaoRepository(db)

    assert config.todas()["proximidade_ativa"] == "0"


def test_fluxo_solicita_permissao_e_obtem_posicao():
    geo = DummyGeolocator()
    resultado = asyncio.run(get_current_position_with_permission(geo))

    assert resultado.ok
    assert resultado.code == "ok"
    assert resultado.permission == "while_in_use"
    assert resultado.position.latitude == -23.588
    assert geo.requested_count == 1


def test_fluxo_detecta_servico_desligado_sem_pedir_permissao():
    geo = DummyGeolocator(enabled=False)
    resultado = asyncio.run(get_current_position_with_permission(geo))

    assert not resultado.ok
    assert resultado.code == "service_disabled"
    assert geo.requested_count == 0


def test_fluxo_detecta_bloqueio_permanente():
    geo = DummyGeolocator(current="DENIED", requested="DENIED_FOREVER")
    resultado = asyncio.run(get_current_position_with_permission(geo))

    assert not resultado.ok
    assert resultado.code == "permission_permanently_denied"
