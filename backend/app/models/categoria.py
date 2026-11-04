from datetime import datetime, timezone

from sqlalchemy import UniqueConstraint

from app import db


class Categoria(db.Model):
    __tablename__ = "categorias"
    __table_args__ = (UniqueConstraint("id_usuario", "nombre", "tipo", name="uq_categoria_usuario_nombre_tipo"),)

    id_categoria = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    nombre = db.Column(db.String(80), nullable=False)
    tipo = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.String(255))
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship("Usuario", back_populates="categorias")
    transacciones = db.relationship("Transaccion", back_populates="categoria")
    presupuestos = db.relationship("Presupuesto", back_populates="categoria")

    def to_dict(self):
        return {
            "id_categoria": self.id_categoria,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "descripcion": self.descripcion,
        }