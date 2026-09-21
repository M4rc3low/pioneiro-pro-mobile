from pioneiro_pro.services.cronometro_service import CronometroService


def test_cronometro_iniciar_pausar_e_zerar(monkeypatch):
    valores = iter([100.0, 130.0, 130.0])
    monkeypatch.setattr(
        "pioneiro_pro.services.cronometro_service.time.monotonic",
        lambda: next(valores),
    )

    cronometro = CronometroService()
    cronometro.iniciar()
    cronometro.pausar()

    assert cronometro.segundos() == 30
    assert cronometro.minutos_para_registro() == 1

    cronometro.zerar()
    assert cronometro.segundos() == 0
    assert cronometro.rodando is False


def test_texto_do_cronometro(monkeypatch):
    valores = iter([10.0, 3671.0])
    monkeypatch.setattr(
        "pioneiro_pro.services.cronometro_service.time.monotonic",
        lambda: next(valores),
    )

    cronometro = CronometroService()
    cronometro.iniciar()

    assert cronometro.texto() == "01:01:01"
