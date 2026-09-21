def formatar_minutos(total_minutos: int) -> str:
    horas, minutos = divmod(max(0, int(total_minutos)), 60)
    if horas and minutos:
        return f"{horas}h {minutos:02d}min"
    if horas:
        return f"{horas}h"
    return f"{minutos}min"
