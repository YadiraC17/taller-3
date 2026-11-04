from datetime import datetime, timezone
from decimal import Decimal

from sqlalchemy import CheckConstraint

from app import db


class Transaccion(db.Model):
    __tablename__ = "transacciones"
    __table_args__ = (CheckConstraint("monto > 0", name="ck_transaccion_monto_positivo"),)

    id_transaccion = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False, index=True)
    tipo = db.Column(db.String(10), nullable=False)
    monto = db.Column(db.Numeric(12, 2), nullable=False)
    moneda = db.Column(db.String(3), nullable=False)
    descripcion = db.Column(db.String(255))
    fecha = db.Column(db.Date, nullable=False, index=True)
    fecha_registro = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship("Usuario", back_populates="transacciones")
    categoria = db.relationship("Categoria", back_populates="transacciones")

    def to_dict(self):
        return {
            "id_transaccion": self.id_transaccion,
            "id_categoria": self.id_categoria,
            "categoria": self.categoria.nombre,
            "tipo": self.tipo,
            "monto": float(Decimal(self.monto)),
            "moneda": self.moneda,
            "descripcion": self.descripcion,
            "fecha": self.fecha.isoformat(),
        }