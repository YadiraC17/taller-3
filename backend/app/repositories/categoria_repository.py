from app.models import Categoria, Presupuesto, Transaccion


def listar(id_usuario, tipo=None):
    query = Categoria.query.filter_by(id_usuario=id_usuario)
    if tipo:
        query = query.filter_by(tipo=tipo)
    return query.order_by(Categoria.nombre.asc()).all()


def obtener(id_usuario, id_categoria):
    return Categoria.query.filter_by(id_usuario=id_usuario, id_categoria=id_categoria).first()


def duplicada(id_usuario, nombre, tipo, excluir=None):
    query = Categoria.query.filter_by(id_usuario=id_usuario, nombre=nombre, tipo=tipo)
    if excluir:
        query = query.filter(Categoria.id_categoria != excluir)
    return query.first() is not None


def tiene_relaciones(id_categoria):
    return (
        Transaccion.query.filter_by(id_categoria=id_categoria).first() is not None
        or Presupuesto.query.filter_by(id_categoria=id_categoria).first() is not None
    )