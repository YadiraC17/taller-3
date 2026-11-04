from sqlalchemy import func

from app.models import Categoria, Transaccion


def resumen(id_usuario, inicio, fin):
    return (
        Transaccion.query.with_entities(
            Transaccion.moneda,
            Transaccion.tipo,
            func.sum(Transaccion.monto),
        )
        .filter(
            Transaccion.id_usuario == id_usuario,
            Transaccion.fecha >= inicio,
            Transaccion.fecha < fin,
        )
        .group_by(Transaccion.moneda, Transaccion.tipo)
        .all()
    )


def gastos_categoria(id_usuario, inicio, fin):
    return (
        Transaccion.query.with_entities(
            Categoria.id_categoria,
            Categoria.nombre,
            Transaccion.moneda,
            func.sum(Transaccion.monto),
        )
        .join(Categoria, Categoria.id_categoria == Transaccion.id_categoria)
        .filter(
            Transaccion.id_usuario == id_usuario,
            Transaccion.tipo == "GASTO",
            Transaccion.fecha >= inicio,
            Transaccion.fecha < fin,
        )
        .group_by(Categoria.id_categoria, Categoria.nombre, Transaccion.moneda)
        .order_by(Categoria.nombre.asc())
        .all()
    )


def evolucion(id_usuario, inicio, fin):
    return (
        Transaccion.query.with_entities(Transaccion.fecha, Transaccion.tipo, Transaccion.moneda, Transaccion.monto)
        .filter(
            Transaccion.id_usuario == id_usuario,
            Transaccion.fecha >= inicio,
            Transaccion.fecha < fin,
        )
        .all()
    )