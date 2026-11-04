from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.routes import api
from app.services import categoria_service
from app.utils.responses import success
from app.utils.validators import json_object


def usuario_id():
    return int(get_jwt_identity())


@api.post("/categorias")
@jwt_required()
def crear_categoria():
    categoria = categoria_service.crear(usuario_id(), json_object())
    return success("Categoría creada correctamente", categoria.to_dict(), 201)


@api.get("/categorias")
@jwt_required()
def listar_categorias():
    categorias = categoria_service.listar(usuario_id(), request.args.get("tipo"))
    return success("Categorías consultadas", [categoria.to_dict() for categoria in categorias])


@api.get("/categorias/<int:id_categoria>")
@jwt_required()
def obtener_categoria(id_categoria):
    categoria = categoria_service.obtener(usuario_id(), id_categoria)
    return success("Categoría consultada", categoria.to_dict())


@api.put("/categorias/<int:id_categoria>")
@jwt_required()
def actualizar_categoria(id_categoria):
    categoria = categoria_service.actualizar(usuario_id(), id_categoria, json_object())
    return success("Categoría actualizada correctamente", categoria.to_dict())


@api.delete("/categorias/<int:id_categoria>")
@jwt_required()
def eliminar_categoria(id_categoria):
    categoria_service.eliminar(usuario_id(), id_categoria)
    return "", 204