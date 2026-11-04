from app.models import Usuario


def por_correo(correo):
    return Usuario.query.filter_by(correo=correo).first()