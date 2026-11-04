from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.models import Usuario
from app.routes import api
from app.services import auth_service
from app.utils.responses import success
from app.utils.validators import json_object


@api.post("/auth/register")
def register():
    usuario = auth_service.registrar(json_object())
    return success("Cuenta creada correctamente", {"usuario": usuario.to_dict()}, 201)


@api.post("/auth/login")
def login():
    usuario = auth_service.autenticar(json_object())
    token = create_access_token(identity=str(usuario.id_usuario))
    return success("Inicio de sesión correcto", {"access_token": token, "usuario": usuario.to_dict()})


@api.get("/auth/me")
@jwt_required()
def me():
    usuario = Usuario.query.get_or_404(int(get_jwt_identity()))
    return success("Usuario autenticado", {"usuario": usuario.to_dict()})


@api.get("/auth/logout")
@jwt_required()
def logout():
    return success("Elimina el token del cliente para cerrar sesión")