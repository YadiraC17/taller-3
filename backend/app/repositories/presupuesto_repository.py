from datetime import date

from sqlalchemy import func

from app.models import Presupuesto, Transaccion


def listar(id_usuario, mes=None, anio=None):
    query = Presupuesto.query.filter_by(id_usuario=id_usuario)
    if mes is not None:
        query = query.filter_by(mes=mes)
    if anio is not None:
        query = query.filter_by(anio=anio)
    return query.order_by(Presupuesto.anio.desc(), Presupuesto.mes.desc()).all()


def obtener(id_usuario, id_presupuesto):
    return Presupuesto.query.filter_by(id_usuario=id_usuario, id_presupuesto=id_presupuesto).first()


def duplicado(id_usuario, id_categoria, moneda, mes, anio, excluir=None):
    query = Presupuesto.query.filter_by(
        id_usuario=id_usuario, id_categoria=id_categoria, moneda=moneda, mes=mes, anio=anio
    )
    if excluir:
        query = query.filter(Presupuesto.id_presupuesto != excluir)
    return query.first() is not None


def gasto_acumulado(presupuesto):
    inicio = date(presupuesto.anio, presupuesto.mes, 1)
    fin = date(presupuesto.anio + (presupuesto.mes == 12), presupuesto.mes % 12 + 1, 1)
    total = (
        Transaccion.query.with_entities(func.coalesce(func.sum(Transaccion.monto), 0))
        .filter(
            Transaccion.id_usuario == presupuesto.id_usuario,
            Transaccion.id_categoria == presupuesto.id_categoria,
            Transaccion.tipo == "GASTO",
            Transaccion.moneda == presupuesto.moneda,
            Transaccion.fecha >= inicio,
            Transaccion.fecha < fin,
        )
        .scalar()
    )
    return total or 0