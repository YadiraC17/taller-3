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
    income_category_id = client.post("/api/categorias", headers=account["headers"], json={
        "nombre": "Freelance",
        "tipo": "INGRESO",
    }).json["data"]["id_categoria"]
    today = date.today()

    transaction = client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 425,
        "moneda": "PEN",
        "fecha": today.isoformat(),
    })
    assert transaction.status_code == 201
    income = client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": income_category_id,
        "tipo": "INGRESO",
        "monto": 200,
        "moneda": "USD",
        "fecha": today.isoformat(),
    })
    assert income.status_code == 201

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
    assert summary["USD"]["ingresos"] == 200
    category_report = client.get(
        f"/api/reportes/gastos-categoria?mes={today.month}&anio={today.year}",
        headers=account["headers"],
    ).json["data"]
    assert category_report == [{
        "id_categoria": category_id,
        "categoria": "Alimentación",
        "moneda": "PEN",
        "total": 425,
    }]
    evolution = client.get(
        f"/api/reportes/evolucion?anio={today.year}",
        headers=account["headers"],
    ).json["data"]["meses"][today.month - 1]
    assert evolution["PEN"]["gastos"] == 425
    assert evolution["USD"]["ingresos"] == 200


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


def test_user_cannot_read_another_users_transaction(client, create_account):
    owner = create_account("Owner")
    other = create_account("Other")
    category_id = create_expense_category(client, owner["headers"])
    created = client.post("/api/transacciones", headers=owner["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 20,
        "moneda": "PEN",
        "fecha": date.today().isoformat(),
    })
    transaction_id = created.json["data"]["id_transaccion"]
    response = client.get(f"/api/transacciones/{transaction_id}", headers=other["headers"])
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


def test_rejects_negative_amount(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    response = client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": -12.5,
        "moneda": "PEN",
        "fecha": date.today().isoformat(),
    })
    assert response.status_code == 400


def test_rejects_invalid_currency_and_category_type_mismatch(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    base_payload = {
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 12,
        "moneda": "EUR",
        "fecha": date.today().isoformat(),
    }
    invalid_currency = client.post("/api/transacciones", headers=account["headers"], json=base_payload)
    assert invalid_currency.status_code == 400

    base_payload.update({"tipo": "INGRESO", "moneda": "PEN"})
    mismatched_type = client.post("/api/transacciones", headers=account["headers"], json=base_payload)
    assert mismatched_type.status_code == 400


def test_transaction_crud_persists_between_requests(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    payload = {
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 10,
        "moneda": "PEN",
        "fecha": date.today().isoformat(),
    }
    created = client.post("/api/transacciones", headers=account["headers"], json=payload)
    transaction_id = created.json["data"]["id_transaccion"]

    fetched = client.get(f"/api/transacciones/{transaction_id}", headers=account["headers"])
    assert fetched.status_code == 200
    assert fetched.json["data"]["monto"] == 10

    payload["monto"] = 14.25
    updated = client.put(f"/api/transacciones/{transaction_id}", headers=account["headers"], json=payload)
    assert updated.status_code == 200
    assert client.get(f"/api/transacciones/{transaction_id}", headers=account["headers"]).json["data"]["monto"] == 14.25

    assert client.delete(f"/api/transacciones/{transaction_id}", headers=account["headers"]).status_code == 204
    assert client.get(f"/api/transacciones/{transaction_id}", headers=account["headers"]).status_code == 404


def test_transaction_filters_by_date_type_currency_and_category(client, create_account):
    account = create_account()
    expense_category_id = create_expense_category(client, account["headers"])
    income_category_id = client.post("/api/categorias", headers=account["headers"], json={
        "nombre": "Sueldo",
        "tipo": "INGRESO",
    }).json["data"]["id_categoria"]
    today = date.today()
    for category_id, kind, amount, currency in (
        (expense_category_id, "GASTO", 12, "PEN"),
        (expense_category_id, "GASTO", 25, "USD"),
        (income_category_id, "INGRESO", 50, "PEN"),
    ):
        assert client.post("/api/transacciones", headers=account["headers"], json={
            "id_categoria": category_id,
            "tipo": kind,
            "monto": amount,
            "moneda": currency,
            "fecha": today.isoformat(),
        }).status_code == 201

    query = (
        f"/api/transacciones?tipo=GASTO&moneda=PEN&categoria={expense_category_id}"
        f"&fecha_inicio={today.isoformat()}&fecha_fin={today.isoformat()}"
    )
    response = client.get(query, headers=account["headers"])
    assert response.status_code == 200
    assert len(response.json["data"]) == 1
    assert response.json["data"][0]["monto"] == 12


def test_transaction_list_is_paginated(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    for amount in (10, 20, 30):
        response = client.post("/api/transacciones", headers=account["headers"], json={
            "id_categoria": category_id,
            "tipo": "GASTO",
            "monto": amount,
            "moneda": "PEN",
            "fecha": date.today().isoformat(),
        })
        assert response.status_code == 201

    first_page = client.get(
        "/api/transacciones?page=1&per_page=2",
        headers=account["headers"],
    )
    assert first_page.status_code == 200
    assert len(first_page.json["data"]) == 2
    assert first_page.json["pagination"] == {
        "page": 1,
        "per_page": 2,
        "total": 3,
        "pages": 2,
        "has_next": True,
        "has_prev": False,
    }

    second_page = client.get(
        "/api/transacciones?page=2&per_page=2",
        headers=account["headers"],
    )
    assert len(second_page.json["data"]) == 1
    assert second_page.json["pagination"]["has_next"] is False

    invalid_page_size = client.get(
        "/api/transacciones?per_page=101",
        headers=account["headers"],
    )
    assert invalid_page_size.status_code == 400


def test_category_duplicate_and_budget_crud(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    duplicate = client.post("/api/categorias", headers=account["headers"], json={
        "nombre": "Alimentación",
        "tipo": "GASTO",
    })
    assert duplicate.status_code == 409
    assert client.get("/api/categorias", headers=account["headers"]).status_code == 200
    updated_category = client.put(f"/api/categorias/{category_id}", headers=account["headers"], json={
        "nombre": "Alimentación",
        "tipo": "GASTO",
        "descripcion": "Gastos diarios",
    })
    assert updated_category.status_code == 200
    assert client.get(f"/api/categorias/{category_id}", headers=account["headers"]).json["data"]["descripcion"] == "Gastos diarios"

    today = date.today()
    payload = {
        "id_categoria": category_id,
        "monto_limite": 300,
        "moneda": "PEN",
        "mes": today.month,
        "anio": today.year,
    }
    created = client.post("/api/presupuestos", headers=account["headers"], json=payload)
    budget_id = created.json["data"]["id_presupuesto"]
    assert client.get(f"/api/presupuestos/{budget_id}", headers=account["headers"]).status_code == 200
    payload["monto_limite"] = 450
    assert client.put(f"/api/presupuestos/{budget_id}", headers=account["headers"], json=payload).status_code == 200
    assert client.get(f"/api/presupuestos/{budget_id}", headers=account["headers"]).json["data"]["monto_limite"] == 450
    assert client.delete(f"/api/presupuestos/{budget_id}", headers=account["headers"]).status_code == 204
    assert client.get(f"/api/presupuestos/{budget_id}", headers=account["headers"]).status_code == 404
    assert client.delete(f"/api/categorias/{category_id}", headers=account["headers"]).status_code == 204
    assert client.get(f"/api/categorias/{category_id}", headers=account["headers"]).status_code == 404


def test_exceeded_budget_reports_negative_available_balance(client, create_account):
    account = create_account()
    category_id = create_expense_category(client, account["headers"])
    today = date.today()
    client.post("/api/transacciones", headers=account["headers"], json={
        "id_categoria": category_id,
        "tipo": "GASTO",
        "monto": 110,
        "moneda": "PEN",
        "fecha": today.isoformat(),
    })
    client.post("/api/presupuestos", headers=account["headers"], json={
        "id_categoria": category_id,
        "monto_limite": 100,
        "moneda": "PEN",
        "mes": today.month,
        "anio": today.year,
    })
    item = client.get(
        f"/api/presupuestos/seguimiento?mes={today.month}&anio={today.year}",
        headers=account["headers"],
    ).json["data"][0]
    assert item["porcentaje_consumido"] == 110
    assert item["saldo_disponible"] == -10
    assert item["estado"] == "EXCEDIDO"