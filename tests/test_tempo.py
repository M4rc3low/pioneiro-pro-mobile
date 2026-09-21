from pioneiro_pro.utils.tempo import formatar_minutos


def test_formatar_minutos_apenas_minutos():
    assert formatar_minutos(45) == "45min"


def test_formatar_minutos_apenas_horas():
    assert formatar_minutos(120) == "2h"


def test_formatar_minutos_horas_e_minutos():
    assert formatar_minutos(135) == "2h 15min"


def test_formatar_minutos_nao_negativo():
    assert formatar_minutos(-10) == "0min"
