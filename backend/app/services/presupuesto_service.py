from decimal import Decimal

from app import db
from app.models import Presupuesto
from app.repositories import categoria_repository, presupuesto_repository
from app.utils.validators import ValidationError, positive_decimal, valid_currency, valid_integer


def listar(id_usuario, mes=None, anio=None):
    return presupuesto_repository.listar(id_usuario, mes, anio)


def obtener(id_usuario, id_presupuesto):
    presupuesto = presupuesto_repository.obtener(id_usuario, id_presupuesto)
    if not presupuesto:
        from flask import abort

        abort(404)
    return presupuesto


def _validar(data, id_usuario, actual=None):
    categoria_id = valid_integer(data.get("id_categoria", actual.id_categoria if actual else None), "id_categoria", minimum=1)
    categoria = categoria_repository.obtener(id_usuario, categoria_id)
    if not categoria:
        raise ValidationError("La categoría no existe o no pertenece al usuario", {"id_categoria": "Categoría no válida"}, status=404)
    if categoria.tipo != "GASTO":
        raise ValidationError("Solo se permiten presupuestos para categorías de gasto", {"id_categoria": "Debe ser una categoría GASTO"})
    monto = positive_decimal(data.get("monto_limite", actual.monto_limite if actual else None), "monto_limite")
    moneda = valid_currency(data.get("moneda", actual.moneda if actual else None))
    mes = valid_integer(data.get("mes", actual.mes if actual else None), "mes", minimum=1, maximum=12)
    anio = valid_integer(data.get("anio", actual.anio if actual else None), "anio", minimum=2000, maximum=9999)
    return categoria_id, monto, moneda, mes, anio


def crear(id_usuario, data):
    valores = _validar(data, id_usuario)
    if presupuesto_repository.duplicado(id_usuario, valores[0], valores[2], valores[3], valores[4]):
        raise ValidationError("Ya existe un presupuesto para esa categoría, moneda y periodo", status=409)
    presupuesto = Presupuesto(
        id_usuario=id_usuario,
        id_categoria=valores[0],
        monto_limite=valores[1],
        moneda=valores[2],
        mes=valores[3],
        anio=valores[4],
    )
    db.session.add(presupuesto)
    db.session.commit()
    return presupuesto


def actualizar(id_usuario, id_presupuesto, data):
    presupuesto = obtener(id_usuario, id_presupuesto)
    valores = _validar(data, id_usuario, presupuesto)
    if presupuesto_repository.duplicado(id_usuario, valores[0], valores[2], valores[3], valores[4], excluir=id_presupuesto):
        raise ValidationError("Ya existe un presupuesto para esa categoría, moneda y periodo", status=409)
    presupuesto.id_categoria, presupuesto.monto_limite, presupuesto.moneda, presupuesto.mes, presupuesto.anio = valores
    db.session.commit()
    return presupuesto


def eliminar(id_usuario, id_presupuesto):
    presupuesto = obtener(id_usuario, id_presupuesto)
    db.session.delete(presupuesto)
    db.session.commit()


def seguimiento(id_usuario, mes=None, anio=None):
    resultados = []
    for presupuesto in listar(id_usuario, mes, anio):
        gasto = Decimal(presupuesto_repository.gasto_acumulado(presupuesto))
        limite = Decimal(presupuesto.monto_limite)
        porcentaje = gasto / limite * Decimal("100")
        estado = "DENTRO_DEL_PRESUPUESTO" if porcentaje < 80 else "CERCA_DEL_LIMITE" if porcentaje < 100 else "EXCEDIDO"
        resultado = presupuesto.to_dict()
        resultado.update({
            "gasto_acumulado": float(gasto),
            "porcentaje_consumido": round(float(porcentaje), 2),
            "saldo_disponible": float(limite - gasto),
            "estado": estado,
        })
        resultados.append(resultado)
    return resultados