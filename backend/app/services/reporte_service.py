from datetime import date
from decimal import Decimal

from app.repositories import reporte_repository
from app.utils.validators import valid_integer


def _periodo(params):
    hoy = date.today()
    mes = valid_integer(params.get("mes", hoy.month), "mes", minimum=1, maximum=12)
    anio = valid_integer(params.get("anio", hoy.year), "anio", minimum=2000, maximum=9998)
    inicio = date(anio, mes, 1)
    fin = date(anio + (mes == 12), mes % 12 + 1, 1)
    return mes, anio, inicio, fin


def resumen(id_usuario, params):
    mes, anio, inicio, fin = _periodo(params)
    datos = {"periodo": {"mes": mes, "anio": anio}}
    filas = reporte_repository.resumen(id_usuario, inicio, fin)
    for moneda in ("PEN", "USD"):
        ingresos = Decimal("0")
        gastos = Decimal("0")
        for moneda_fila, tipo, monto in filas:
            if moneda_fila == moneda:
                if tipo == "INGRESO":
                    ingresos = Decimal(monto)
                elif tipo == "GASTO":
                    gastos = Decimal(monto)
        datos[moneda] = {
            "ingresos": float(ingresos),
            "gastos": float(gastos),
            "balance": float(ingresos - gastos),
        }
    return datos


def gastos_categoria(id_usuario, params):
    _mes, _anio, inicio, fin = _periodo(params)
    return [
        {
            "id_categoria": id_categoria,
            "categoria": nombre,
            "moneda": moneda,
            "total": float(monto),
        }
        for id_categoria, nombre, moneda, monto in reporte_repository.gastos_categoria(id_usuario, inicio, fin)
    ]


def evolucion(id_usuario, params):
    anio = valid_integer(params.get("anio", date.today().year), "anio", minimum=2000, maximum=9998)
    inicio = date(anio, 1, 1)
    fin = date(anio + 1, 1, 1)
    valores = {
        (mes, moneda, tipo): Decimal("0")
        for mes in range(1, 13)
        for moneda in ("PEN", "USD")
        for tipo in ("INGRESO", "GASTO")
    }
    for fecha, tipo, moneda, monto in reporte_repository.evolucion(id_usuario, inicio, fin):
        valores[(fecha.month, moneda, tipo)] += Decimal(monto)
    return [
        {
            "mes": mes,
            "PEN": {tipo.lower() + "s": float(valores[(mes, "PEN", tipo)]) for tipo in ("INGRESO", "GASTO")},
            "USD": {tipo.lower() + "s": float(valores[(mes, "USD", tipo)]) for tipo in ("INGRESO", "GASTO")},
        }
        for mes in range(1, 13)
    ]