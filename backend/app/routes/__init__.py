from flask import Blueprint

api = Blueprint("api", __name__)

from app.routes import auth_routes, categoria_routes, presupuesto_routes, reporte_routes, transaccion_routes