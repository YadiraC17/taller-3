from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.routes import api
from app.services import presupuesto_service
from app.utils.responses import success
from app.utils.validators import json_object, valid_integer


def usuario_id():
    return int(get_jwt_identity())


def periodo():
    mes = request.args.get("mes")
    anio = request.args.get("anio")
    return (
        valid_integer(mes, "mes", minimum=1, maximum=12) if mes else None,
        valid_integer(anio, "anio", minimum=2000, maximum=9999) if anio else None,
    )


@api.post("/presupuestos")
@jwt_required()
def crear_presupuesto():
    presupuesto = presupuesto_service.crear(usuario_id(), json_object())
    return success("Presupuesto creado correctamente", presupuesto.to_dict(), 201)


@api.get("/presupuestos")
@jwt_required()
def listar_presupuestos():
    mes, anio = periodo()
    items = presupuesto_service.listar(usuario_id(), mes, anio)
    return success("Presupuestos consultados", [item.to_dict() for item in items])


@api.get("/presupuestos/seguimiento")
@jwt_required()
def seguimiento_presupuestos():
    mes, anio = periodo()
    return success("Seguimiento presupuestario calculado", presupuesto_service.seguimiento(usuario_id(), mes, anio))


@api.get("/presupuestos/<int:id_presupuesto>")
@jwt_required()
def obtener_presupuesto(id_presupuesto):
    item = presupuesto_service.obtener(usuario_id(), id_presupuesto)
    return success("Presupuesto consultado", item.to_dict())


@api.put("/presupuestos/<int:id_presupuesto>")
@jwt_required()
def actualizar_presupuesto(id_presupuesto):
    item = presupuesto_service.actualizar(usuario_id(), id_presupuesto, json_object())
    return success("Presupuesto actualizado correctamente", item.to_dict())


@api.delete("/presupuestos/<int:id_presupuesto>")
@jwt_required()
def eliminar_presupuesto(id_presupuesto):
    presupuesto_service.eliminar(usuario_id(), id_presupuesto)
    return "", 204