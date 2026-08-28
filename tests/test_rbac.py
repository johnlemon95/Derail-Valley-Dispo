"""Tests for RBAC – verifies role-based access control on service and route level."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from backend.main import app
from backend.services.auth_service import create_token

client = TestClient(app)

ADMIN_TOKEN = create_token(player_id=1, username="admin", role="Admin")
OPERATOR_TOKEN = create_token(player_id=2, username="player_b", role="Operator")


def auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def test_operator_cannot_create_job():
    resp = client.post(
        "/api/admin/jobs",
        json={
            "title": "Test Job",
            "job_type": "FR",
            "origin_track": "GF-A1L",
            "destination_track": "CS-B2S",
            "reward": 100,
        },
        headers=auth(OPERATOR_TOKEN),
    )
    assert resp.status_code == 403


def test_admin_can_reach_users_endpoint():
    with patch("backend.api.admin_routes.repo.get_users", return_value=[]):
        resp = client.get("/api/admin/users", headers=auth(ADMIN_TOKEN))
    assert resp.status_code == 200


def test_unauthenticated_request_rejected():
    resp = client.get("/api/jobs/")
    assert resp.status_code == 401


def test_operator_can_list_jobs():
    with patch("backend.api.job_routes.repo.get_jobs", return_value=[]):
        resp = client.get("/api/jobs/", headers=auth(OPERATOR_TOKEN))
    assert resp.status_code == 200


def test_operator_cannot_delete_job():
    resp = client.delete("/api/admin/jobs/1", headers=auth(OPERATOR_TOKEN))
    assert resp.status_code == 403


def test_operator_cannot_create_user():
    resp = client.post(
        "/api/admin/users",
        json={"username": "hack", "display_name": "Hacker", "password": "pw", "role": "Admin"},
        headers=auth(OPERATOR_TOKEN),
    )
    assert resp.status_code == 403
