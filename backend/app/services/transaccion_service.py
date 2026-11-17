from app import db
from app.models import Transaccion
from app.repositories import categoria_repository, transaccion_repository
from app.utils.validators import (
    ValidationError,
    positive_decimal,
    valid_currency,
    valid_date,
    valid_integer,
    valid_type,
)


def listar(id_usuario, params):
    filtros = {}
    page = valid_integer(params.get("page", 1), "page", minimum=1)
    per_page = valid_integer(params.get("per_page", 50), "per_page", minimum=1, maximum=100)
    if params.get("tipo"):
        filtros["tipo"] = valid_type(params["tipo"])
    if params.get("moneda"):
        filtros["moneda"] = valid_currency(params["moneda"])
    if params.get("categoria"):
        filtros["categoria"] = valid_integer(params["categoria"], "categoria", minimum=1)
    for field in ("fecha_inicio", "fecha_fin"):
        if params.get(field):
            filtros[field] = valid_date(params[field], field)
    if filtros.get("fecha_inicio") and filtros.get("fecha_fin") and filtros["fecha_inicio"] > filtros["fecha_fin"]:
        raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin")
    pagination = transaccion_repository.listar(id_usuario, filtros, page, per_page)
    metadata = {
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }
    return pagination.items, metadata


def obtener(id_usuario, id_transaccion):
    transaccion = transaccion_repository.obtener(id_usuario, id_transaccion)
    if not transaccion:
        from flask import abort

        abort(404)
    return transaccion


def _datos_transaccion(data, id_usuario, actual=None):
    tipo = valid_type(data.get("tipo", actual.tipo if actual else None))
    categoria_id = valid_integer(data.get("id_categoria", actual.id_categoria if actual else None), "id_categoria", minimum=1)
    categoria = categoria_repository.obtener(id_usuario, categoria_id)
    if not categoria:
        raise ValidationError("La categoría no existe o no pertenece al usuario", {"id_categoria": "Categoría no válida"}, status=404)
    if categoria.tipo != tipo:
        raise ValidationError("El tipo de categoría debe coincidir con el tipo de transacción", {"tipo": "No coincide con la categoría"})
    monto = positive_decimal(data.get("monto", actual.monto if actual else None), "monto")
    moneda = valid_currency(data.get("moneda", actual.moneda if actual else None))
    fecha = valid_date(data.get("fecha", actual.fecha.isoformat() if actual else None))
    descripcion = data.get("descripcion", actual.descripcion if actual else None)
    if descripcion is not None and (not isinstance(descripcion, str) or len(descripcion) > 255):
        raise ValidationError("La descripción no puede superar 255 caracteres", {"descripcion": "Valor no válido"})
    return categoria_id, tipo, monto, moneda, fecha, descripcion or None


def crear(id_usuario, data):
    valores = _datos_transaccion(data, id_usuario)
    transaccion = Transaccion(
        id_usuario=id_usuario,
        id_categoria=valores[0],
        tipo=valores[1],
        monto=valores[2],
        moneda=valores[3],
        fecha=valores[4],
        descripcion=valores[5],
    )
    db.session.add(transaccion)
    db.session.commit()
    return transaccion


def actualizar(id_usuario, id_transaccion, data):
    transaccion = obtener(id_usuario, id_transaccion)
    valores = _datos_transaccion(data, id_usuario, transaccion)
    transaccion.id_categoria, transaccion.tipo, transaccion.monto, transaccion.moneda, transaccion.fecha, transaccion.descripcion = valores
    db.session.commit()
    return transaccion


def eliminar(id_usuario, id_transaccion):
    transaccion = obtener(id_usuario, id_transaccion)
    db.session.delete(transaccion)
    db.session.commit()