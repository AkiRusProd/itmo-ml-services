from __future__ import annotations

import sys
import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Iterator

import httpx
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.db.base import Base
from app.models import prediction_request, prediction_result, promo_code, promo_code_activation, transaction, user, wallet  # noqa: F401
from app.schemas.auth import RegisterRequest
from app.services.auth_service import AuthService


@pytest.fixture()
def db_session(tmp_path: Path) -> Iterator[Session]:
    db_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{db_path}",
        future=True,
        connect_args={"check_same_thread": False},
    )
    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        class_=Session,
    )

    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture()
def auth_service(db_session: Session) -> AuthService:
    return AuthService(db_session)


@pytest.fixture()
def regular_user(auth_service: AuthService):
    return auth_service.register_user(
        RegisterRequest(
            email="user@example.com",
            password="strongpass123",
            full_name="Regular User",
        )
    )


@pytest.fixture()
def admin_user(auth_service: AuthService):
    admin = auth_service.register_user(
        RegisterRequest(
            email="admin@example.com",
            password="strongpass123",
            full_name="Admin User",
        )
    )
    admin.role = "admin"
    auth_service.db.commit()
    auth_service.db.refresh(admin)
    return admin


def _find_free_port() -> int:
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind(("127.0.0.1", 0))
            return sock.getsockname()[1]
    except PermissionError as exc:
        pytest.skip(f"Local socket binding is unavailable in this environment: {exc}")


@pytest.fixture()
def client(tmp_path: Path) -> Iterator[httpx.Client]:
    db_path = tmp_path / "integration.db"
    port = _find_free_port()
    env = os.environ.copy()
    env["DATABASE_URL"] = f"sqlite:///{db_path}"
    env["CELERY_TASK_ALWAYS_EAGER"] = "true"

    process = subprocess.Popen(
        [
            str(ROOT_DIR / ".venv" / "bin" / "uvicorn"),
            "app.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            str(port),
        ],
        cwd=ROOT_DIR,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    base_url = f"http://127.0.0.1:{port}"
    with httpx.Client(base_url=base_url, timeout=10.0) as test_client:
        deadline = time.time() + 20
        while time.time() < deadline:
            try:
                response = test_client.get("/api/v1/health")
                if response.status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            time.sleep(0.2)
        else:
            process.terminate()
            process.wait(timeout=5)
            raise RuntimeError("Uvicorn test server did not start in time.")

        try:
            yield test_client
        finally:
            process.terminate()
            process.wait(timeout=5)


@pytest.fixture()
def auth_headers(client: httpx.Client) -> dict[str, str]:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "api-user@example.com",
            "password": "strongpass123",
            "full_name": "API User",
        },
    )
    assert register_response.status_code == 201

    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "api-user@example.com",
            "password": "strongpass123",
        },
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
