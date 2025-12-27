import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json

from sqlalchemy import select

from app import User, app, db


def login_client(client, username="testuser", password="password"):
    # create user if not exists
    with app.app_context():
        u = db.session.scalars(select(User).filter_by(username=username)).first()
        if not u:
            u = User(username=username, email=f"{username}@example.com")
            u.set_password(password)
            db.session.add(u)
            db.session.commit()
    resp = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
    return resp


def test_valid_interfaces():
    client = app.test_client()
    login_client(client)
    payload = {
        "hostname": "R1",
        "interfaces": [
            {"name": "G0/0", "ip": "192.168.10.1/24"},
            {"name": "Loop0", "ip": "10.0.0.1"},
        ],
    }
    r = client.post("/api/lab/1/device/R1/config", json=payload)
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("success") is True


def test_invalid_ip_rejected():
    client = app.test_client()
    login_client(client)
    payload = {"interfaces": [{"name": "G0/1", "ip": "999.999.999.999"}]}
    r = client.post("/api/lab/1/device/R1/config", json=payload)
    assert r.status_code == 400
    data = r.get_json()
    assert "errors" in data
    assert any("invalid ip" in e.lower() for e in data["errors"])


def test_empty_name_rejected():
    client = app.test_client()
    login_client(client)
    payload = {"interfaces": [{"name": "", "ip": "192.168.1.1"}]}
    r = client.post("/api/lab/1/device/R1/config", json=payload)
    assert r.status_code == 400
    data = r.get_json()
    assert "errors" in data
    assert any("missing name" in e.lower() for e in data["errors"])
