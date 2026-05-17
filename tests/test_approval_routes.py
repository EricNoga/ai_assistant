from fastapi.testclient import TestClient

from backend.api.app import create_app


client = TestClient(
    create_app()
)


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
    response = client.get("/approvals")

    assert response.status_code == 200

    data = response.json()

    assert "approvals" in data
    assert isinstance(data["approvals"], list)


def test_approval_detail_endpoint():
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
    approval_id = _create_high_risk_approval()

    response = client.post(
        f"/approvals/{approval_id}/execute"
    )

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "Approval must be approved before execution"


def test_execute_approved_tool_request():
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


def test_approve_missing_approval():
    response = client.post(
        "/approvals/not-real/approve"
    )

    assert response.status_code == 200

    data = response.json()

    assert "error" in data
    assert data["error"] == "Approval not found"