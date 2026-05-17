from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


def _clear_approval_state():
    response = client.post(
        "/test-admin/clear-approvals"
    )

    assert response.status_code == 200


def _create_high_risk_approval():
    response = client.post(
        "/tools/run",
        json={
            "tool_name": "run_python_code",
            "args": {
                "code": "print('approval test')"
            }
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "result" in data
    assert data["result"]["blocked"] is True
    assert "approval_id" in data["result"]

    return data["result"]["approval_id"]


def test_approvals_endpoint():
    _clear_approval_state()

    response = client.get("/approvals")

    assert response.status_code == 200

    data = response.json()

    assert "approvals" in data
    assert isinstance(data["approvals"], list)


def test_approval_audit_endpoint():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.get("/approvals/audit")

    assert response.status_code == 200

    data = response.json()

    assert "events" in data
    assert isinstance(data["events"], list)

    assert any(
        event["approval_id"] == approval_id
        for event in data["events"]
    )


def test_approval_specific_audit_endpoint():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.get(
        f"/approvals/{approval_id}/audit"
    )

    assert response.status_code == 200

    data = response.json()

    assert "events" in data
    assert isinstance(data["events"], list)

    assert all(
        event["approval_id"] == approval_id
        for event in data["events"]
    )

    assert any(
        event["action"] == "created"
        for event in data["events"]
    )


def test_approval_detail_endpoint():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.get(
        f"/approvals/{approval_id}"
    )

    assert response.status_code == 200

    data = response.json()

    assert "approval" in data
    assert data["approval"]["id"] == approval_id
    assert data["approval"]["status"] == "pending"


def test_approve_approval_endpoint():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.post(
        f"/approvals/{approval_id}/approve"
    )

    assert response.status_code == 200

    data = response.json()

    assert "approval" in data
    assert data["approval"]["id"] == approval_id
    assert data["approval"]["status"] == "approved"


def test_deny_approval_endpoint():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.post(
        f"/approvals/{approval_id}/deny"
    )

    assert response.status_code == 200

    data = response.json()

    assert "approval" in data
    assert data["approval"]["id"] == approval_id
    assert data["approval"]["status"] == "denied"


def test_execute_approval_requires_approval_first():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "Approval must be approved before execution"


def test_execute_approved_tool_request():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    approve_response = client.post(
        f"/approvals/{approval_id}/approve"
    )

    assert approve_response.status_code == 200

    execute_response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert execute_response.status_code == 200

    data = execute_response.json()

    assert "approval" in data
    assert "result" in data
    assert data["approval"]["status"] == "executed"
    assert data["result"]["returncode"] == 0
    assert "approval test" in data["result"]["stdout"]


def test_approval_cannot_execute_twice():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    approve_response = client.post(
        f"/approvals/{approval_id}/approve"
    )

    assert approve_response.status_code == 200

    first_execute_response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert first_execute_response.status_code == 200

    second_execute_response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert second_execute_response.status_code == 200

    data = second_execute_response.json()

    assert "error" in data
    assert data["error"] == "Approval has already been executed"


def test_denied_approval_cannot_execute():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    deny_response = client.post(
        f"/approvals/{approval_id}/deny"
    )

    assert deny_response.status_code == 200

    execute_response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert execute_response.status_code == 200

    data = execute_response.json()

    assert "error" in data
    assert data["error"] == "Denied approval cannot be executed"


def test_denied_approval_cannot_be_approved():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    deny_response = client.post(
        f"/approvals/{approval_id}/deny"
    )

    assert deny_response.status_code == 200

    approve_response = client.post(
        f"/approvals/{approval_id}/approve"
    )

    assert approve_response.status_code == 200

    data = approve_response.json()

    assert "error" in data
    assert data["error"] == "Approval has been denied and cannot be approved"


def test_executed_approval_cannot_be_denied():
    _clear_approval_state()

    approval_id = _create_high_risk_approval()

    approve_response = client.post(
        f"/approvals/{approval_id}/approve"
    )

    assert approve_response.status_code == 200

    execute_response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert execute_response.status_code == 200

    deny_response = client.post(
        f"/approvals/{approval_id}/deny"
    )

    assert deny_response.status_code == 200

    data = deny_response.json()

    assert "error" in data
    assert data["error"] == "Only pending approvals can be denied"


def test_approve_missing_approval():
    _clear_approval_state()

    response = client.post(
        "/approvals/not-real/approve"
    )

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "Approval not found"