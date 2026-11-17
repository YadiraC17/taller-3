from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.routes import api
from app.services import transaccion_service
from app.utils.responses import success
from app.utils.validators import json_object


def usuario_id():
    return int(get_jwt_identity())


@api.post("/transacciones")
@jwt_required()
def crear_transaccion():
    transaccion = transaccion_service.crear(usuario_id(), json_object())
    return success("Transacción registrada correctamente", transaccion.to_dict(), 201)


@api.get("/transacciones")
@jwt_required()
def listar_transacciones():
    transacciones, pagination = transaccion_service.listar(usuario_id(), request.args)
    return success(
        "Transacciones consultadas",
        [item.to_dict() for item in transacciones],
        pagination=pagination,
    )


@api.get("/transacciones/<int:id_transaccion>")
@jwt_required()
def obtener_transaccion(id_transaccion):
    transaccion = transaccion_service.obtener(usuario_id(), id_transaccion)
    return success("Transacción consultada", transaccion.to_dict())


@api.put("/transacciones/<int:id_transaccion>")
@jwt_required()
def actualizar_transaccion(id_transaccion):
    transaccion = transaccion_service.actualizar(usuario_id(), id_transaccion, json_object())
    return success("Transacción actualizada correctamente", transaccion.to_dict())


@api.delete("/transacciones/<int:id_transaccion>")
@jwt_required()
def eliminar_transaccion(id_transaccion):
    transaccion_service.eliminar(usuario_id(), id_transaccion)
    return "", 204