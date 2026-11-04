from datetime import date
from decimal import Decimal, InvalidOperation


TIPOS = {"INGRESO", "GASTO"}
MONEDAS = {"PEN", "USD"}


class ValidationError(ValueError):
    def __init__(self, message, errors=None, status=400):
        super().__init__(message)
        self.errors = errors or {}
        self.status = status


def json_object():
    from flask import request

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        raise ValidationError("Se requiere un objeto JSON válido")
    return data


def required_text(data, field, max_length, label=None):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"El campo {label or field} es obligatorio", {field: "Campo obligatorio"})
    value = value.strip()
    if len(value) > max_length:
        raise ValidationError(f"El campo {label or field} supera el máximo permitido", {field: f"Máximo {max_length} caracteres"})
    return value


def positive_decimal(value, field):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("El monto debe ser un número válido", {field: "Valor no válido"})
    if not amount.is_finite() or amount <= 0 or amount.as_tuple().exponent < -2:
        raise ValidationError("El monto debe ser mayor que cero y tener hasta dos decimales", {field: "Valor no válido"})
    return amount.quantize(Decimal("0.01"))


def valid_type(value, field="tipo"):
    normalized = str(value or "").upper()
    if normalized not in TIPOS:
        raise ValidationError("El tipo debe ser INGRESO o GASTO", {field: "Tipo no válido"})
    return normalized


def valid_currency(value):
    normalized = str(value or "").upper()
    if normalized not in MONEDAS:
        raise ValidationError("La moneda debe ser PEN o USD", {"moneda": "Moneda no válida"})
    return normalized


def valid_date(value, field="fecha"):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        raise ValidationError("La fecha debe tener formato YYYY-MM-DD", {field: "Fecha no válida"})


def valid_integer(value, field, minimum=None, maximum=None):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"El campo {field} debe ser un entero", {field: "Valor no válido"})
    if minimum is not None and number < minimum or maximum is not None and number > maximum:
        raise ValidationError(f"El campo {field} está fuera de rango", {field: "Valor fuera de rango"})
    return number