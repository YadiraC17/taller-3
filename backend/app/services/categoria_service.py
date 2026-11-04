from app import db
from app.models import Categoria
from app.repositories import categoria_repository as repository
from app.utils.validators import ValidationError, required_text, valid_type


def listar(id_usuario, tipo=None):
    if tipo:
        tipo = valid_type(tipo)
    return repository.listar(id_usuario, tipo)


def obtener(id_usuario, id_categoria):
    categoria = repository.obtener(id_usuario, id_categoria)
    if not categoria:
        from flask import abort

        abort(404)
    return categoria


def crear(id_usuario, data):
    nombre = required_text(data, "nombre", 80)
    tipo = valid_type(data.get("tipo"))
    descripcion = data.get("descripcion")
    if descripcion is not None and (not isinstance(descripcion, str) or len(descripcion) > 255):
        raise ValidationError("La descripción no puede superar 255 caracteres", {"descripcion": "Valor no válido"})
    if repository.duplicada(id_usuario, nombre, tipo):
        raise ValidationError("Ya existe una categoría con ese nombre y tipo", status=409)
    categoria = Categoria(id_usuario=id_usuario, nombre=nombre, tipo=tipo, descripcion=descripcion or None)
    db.session.add(categoria)
    db.session.commit()
    return categoria


def actualizar(id_usuario, id_categoria, data):
    categoria = obtener(id_usuario, id_categoria)
    nombre = required_text(data, "nombre", 80)
    tipo = valid_type(data.get("tipo"))
    descripcion = data.get("descripcion")
    if descripcion is not None and (not isinstance(descripcion, str) or len(descripcion) > 255):
        raise ValidationError("La descripción no puede superar 255 caracteres", {"descripcion": "Valor no válido"})
    if repository.duplicada(id_usuario, nombre, tipo, excluir=id_categoria):
        raise ValidationError("Ya existe una categoría con ese nombre y tipo", status=409)
    if tipo != categoria.tipo and (categoria.transacciones or categoria.presupuestos):
        raise ValidationError("No se puede cambiar el tipo de una categoría con movimientos asociados", status=409)
    categoria.nombre = nombre
    categoria.tipo = tipo
    categoria.descripcion = descripcion or None
    db.session.commit()
    return categoria


def eliminar(id_usuario, id_categoria):
    categoria = obtener(id_usuario, id_categoria)
    if repository.tiene_relaciones(id_categoria):
        raise ValidationError("No se puede eliminar una categoría con transacciones o presupuestos", status=409)
    db.session.delete(categoria)
    db.session.commit()