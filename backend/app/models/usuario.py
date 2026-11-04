from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from app import db


class Usuario(db.Model):
    __tablename__ = "usuarios"

    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    activo = db.Column(db.Boolean, nullable=False, default=True)

    categorias = db.relationship("Categoria", back_populates="usuario")
    transacciones = db.relationship("Transaccion", back_populates="usuario")
    presupuestos = db.relationship("Presupuesto", back_populates="usuario")

    def establecer_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verificar_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id_usuario": self.id_usuario,
            "nombre": self.nombre,
            "correo": self.correo,
            "fecha_registro": self.fecha_registro.isoformat(),
        }