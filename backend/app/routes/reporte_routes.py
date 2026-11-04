from flask import request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.routes import api
from app.services import reporte_service
from app.utils.responses import success


@api.get("/reportes/resumen")
@jwt_required()
def resumen():
    data = reporte_service.resumen(int(get_jwt_identity()), request.args)
    return success("Resumen financiero calculado", data)


@api.get("/reportes/gastos-categoria")
@jwt_required()
def gastos_categoria():
    data = reporte_service.gastos_categoria(int(get_jwt_identity()), request.args)
    return success("Distribución de gastos calculada", data)


@api.get("/reportes/evolucion")
@jwt_required()
def evolucion():
    data = reporte_service.evolucion(int(get_jwt_identity()), request.args)
    return success("Evolución financiera calculada", {"anio": request.args.get("anio"), "meses": data})