from datetime import date


def create_expense_category(client, headers, name="Alimentación"):
    response = client.post("/api/categorias", headers=headers, json={
        "nombre": name,
        "tipo": "GASTO",
    })
    assert response.status_code == 201
    return response.json["data"]["id_categoria"]


def test_transaction_budget_tracking_and_report(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    today = date.today()

    transaction = client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 425,
        "moneda": "PEN",
        "fecha": today.isoformat(),
    })
    assert transaction.status_code == 201

    budget = client.post("/api/presupuestos", headers=account["headers"], json={
        "id_categoria": category_id,
        "monto_limite": 500,
        "moneda": "PEN",
        "mes": today.month,
        "anio": today.year,
    })
    assert budget.status_code == 201

    tracking = client.get(
        f"/api/presupuestos/seguimiento?mes={today.month}&anio={today.year}",
        headers=account["headers"],
    ).json["data"][0]
    assert tracking["gasto_acumulado"] == 425
    assert tracking["porcentaje_consumido"] == 85
    assert tracking["estado"] == "CERCA_DEL_LIMITE"

    summary = client.get(
        f"/api/reportes/resumen?mes={today.month}&anio={today.year}",
        headers=account["headers"],
    ).json["data"]
    assert summary["PEN"]["gastos"] == 425
    assert summary["PEN"]["balance"] == -425
    assert summary["USD"]["gastos"] == 0


def test_user_cannot_use_another_users_category(client, create_account):
    owner = create_account("Owner")
    other = create_account("Other")
    category_id = create_expense_category(client, owner["headers"])

    response = client.post("/api/transacciones", headers=other["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 20,
        "moneda": "USD",
        "fecha": date.today().isoformat(),
    })
    assert response.status_code == 404


def test_rejects_nonpositive_amount_and_duplicate_budget(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    invalid = client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 0,
        "moneda": "PEN",
        "fecha": date.today().isoformat(),
    })
    assert invalid.status_code == 400

    today = date.today()
    payload = {
        "id_categoria": category_id,
        "monto_limite": 300,
        "moneda": "PEN",
        "mes": today.month,
        "anio": today.year,
    }
    assert client.post("/api/presupuestos", headers=account["headers"], json=payload).status_code == 201
    assert client.post("/api/presupuestos", headers=account["headers"], json=payload).status_code == 409


def test_category_with_movements_cannot_be_deleted(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 8,
        "moneda": "PEN",
        "fecha": date.today().isoformat(),
    })
    response = client.delete(f"/api/categorias/{category_id}", headers=account["headers"])
    assert response.status_code == 409