from app.models import Transaccion


def listar(id_usuario, filtros):
    query = Transaccion.query.filter_by(id_usuario=id_usuario)
    if filtros.get("tipo"):
        query = query.filter_by(tipo=filtros["tipo"])
    if filtros.get("moneda"):
        query = query.filter_by(moneda=filtros["moneda"])
    if filtros.get("categoria"):
        query = query.filter_by(id_categoria=filtros["categoria"])
    if filtros.get("fecha_inicio"):
        query = query.filter(Transaccion.fecha >= filtros["fecha_inicio"])
    if filtros.get("fecha_fin"):
        query = query.filter(Transaccion.fecha <= filtros["fecha_fin"])
    return query.order_by(Transaccion.fecha.desc(), Transaccion.id_transaccion.desc()).all()


def obtener(id_usuario, id_transaccion):
    return Transaccion.query.filter_by(id_usuario=id_usuario, id_transaccion=id_transaccion).first()