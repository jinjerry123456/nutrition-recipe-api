def _auth_headers(client):
    token_resp = client.post(
        "/auth/token",
        data={"username": "student", "password": "coursework123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert token_resp.status_code == 200
    token = token_resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_combo_crud_flow(client):
    create_payload = {
        "name": "High Protein Combo",
        "description": "For gym day",
        "items": [{"item_id": 1, "quantity": 2}, {"item_id": 2, "quantity": 1}],
    }
    headers = _auth_headers(client)

    create_resp = client.post("/combos", json=create_payload, headers=headers)
    assert create_resp.status_code == 201
    created = create_resp.json()
    combo_id = created["id"]
    assert created["total_calories"] == 1160.0
    assert created["total_protein"] == 60.0
    assert len(created["items"]) == 2

    list_resp = client.get("/combos")
    assert list_resp.status_code == 200
    assert len(list_resp.json()) == 1

    get_resp = client.get(f"/combos/{combo_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "High Protein Combo"

    update_resp = client.put(
        f"/combos/{combo_id}",
        json={"description": "Updated", "items": [{"item_id": 1, "quantity": 1}]},
        headers=headers,
    )
    assert update_resp.status_code == 200
    updated = update_resp.json()
    assert updated["description"] == "Updated"
    assert updated["total_calories"] == 420.0
    assert updated["total_protein"] == 23.0

    delete_resp = client.delete(f"/combos/{combo_id}", headers=headers)
    assert delete_resp.status_code == 204

    missing_resp = client.get(f"/combos/{combo_id}")
    assert missing_resp.status_code == 404


def test_authentication_required_for_write_endpoints(client):
    payload = {
        "name": "No Auth Combo",
        "description": "Should fail",
        "items": [{"item_id": 1, "quantity": 1}],
    }
    response = client.post("/combos", json=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_combo_with_invalid_item_id_returns_404(client):
    payload = {
        "name": "Invalid Item Combo",
        "description": "Should return not found",
        "items": [{"item_id": 999, "quantity": 1}],
    }
    response = client.post("/combos", json=payload, headers=_auth_headers(client))
    assert response.status_code == 404
    assert "Item 999 not found" in response.json()["detail"]


def test_request_validation_for_quantity(client):
    payload = {
        "name": "Bad Quantity",
        "description": "Validation check",
        "items": [{"item_id": 1, "quantity": 0}],
    }
    response = client.post("/combos", json=payload, headers=_auth_headers(client))
    assert response.status_code == 422


def test_analytics_endpoints(client):
    headers = _auth_headers(client)
    client.post(
        "/combos",
        json={
            "name": "A",
            "description": "First combo",
            "items": [{"item_id": 1, "quantity": 1}],
        },
        headers=headers,
    )
    client.post(
        "/combos",
        json={
            "name": "B",
            "description": "Second combo",
            "items": [{"item_id": 2, "quantity": 2}],
        },
        headers=headers,
    )

    summary_resp = client.get("/analytics/category-summary")
    assert summary_resp.status_code == 200
    summary_data = summary_resp.json()
    assert len(summary_data) == 1
    assert summary_data[0]["category_name"] == "Burgers"

    scoreboard_resp = client.get("/analytics/combo-scoreboard")
    assert scoreboard_resp.status_code == 200
    scoreboard = scoreboard_resp.json()
    assert len(scoreboard) == 2
    assert scoreboard[0]["protein_density"] >= scoreboard[1]["protein_density"]


def test_login_failure(client):
    response = client.post(
        "/auth/token",
        data={"username": "student", "password": "wrong-password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401


def test_get_current_user(client):
    headers = _auth_headers(client)
    response = client.get("/auth/me", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == "student"
