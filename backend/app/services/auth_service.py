import re

from app import db
from app.models import Usuario
from app.repositories.usuario_repository import por_correo
from app.utils.validators import ValidationError, required_text


def registrar(data):
    nombre = required_text(data, "nombre", 100)
    correo = required_text(data, "correo", 150).lower()
    password = data.get("password")
    if not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", correo):
        raise ValidationError("El correo electrónico no es válido", {"correo": "Correo no válido"})
    if not isinstance(password, str) or len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres", {"password": "Mínimo 8 caracteres"})
    if por_correo(correo):
        raise ValidationError("El correo electrónico ya está registrado", {"correo": "Correo duplicado"}, status=409)
    usuario = Usuario(nombre=nombre, correo=correo)
    usuario.establecer_password(password)
    db.session.add(usuario)
    db.session.commit()
    return usuario


def autenticar(data):
    correo = str(data.get("correo", "")).strip().lower()
    password = data.get("password")
    usuario = por_correo(correo)
    if not usuario or not usuario.activo or not isinstance(password, str) or not usuario.verificar_password(password):
        raise ValidationError("Correo o contraseña incorrectos", status=401)
    return usuario