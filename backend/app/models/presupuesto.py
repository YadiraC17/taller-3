from datetime import datetime, timezone

from sqlalchemy import CheckConstraint, UniqueConstraint

from app import db


class Presupuesto(db.Model):
    __tablename__ = "presupuestos"
    __table_args__ = (
        UniqueConstraint("id_usuario", "id_categoria", "moneda", "mes", "anio", name="uq_presupuesto_periodo"),
        CheckConstraint("monto_limite > 0", name="ck_presupuesto_monto_positivo"),
    )

    id_presupuesto = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey("usuarios.id_usuario"), nullable=False, index=True)
    id_categoria = db.Column(db.Integer, db.ForeignKey("categorias.id_categoria"), nullable=False, index=True)
    monto_limite = db.Column(db.Numeric(12, 2), nullable=False)
    moneda = db.Column(db.String(3), nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    anio = db.Column(db.Integer, nullable=False)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    usuario = db.relationship("Usuario", back_populates="presupuestos")
    categoria = db.relationship("Categoria", back_populates="presupuestos")

    def to_dict(self):
        return {
            "id_presupuesto": self.id_presupuesto,
            "id_categoria": self.id_categoria,
            "categoria": self.categoria.nombre,
            "monto_limite": float(self.monto_limite),
            "moneda": self.moneda,
            "mes": self.mes,
            "anio": self.anio,
        }