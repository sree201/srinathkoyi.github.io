import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json

from sqlalchemy import select

from app import app, db

with app.test_client() as client:
    with app.app_context():
        from app import User

        u = db.session.scalars(select(User).filter_by(username="smoketest")).first()
        if not u:
            u = User(username="smoketest", email="smoketest@example.com")
            u.set_password("password")
            db.session.add(u)
            db.session.commit()
    resp = client.post(
        "/login",
        data={"username": "smoketest", "password": "password"},
        follow_redirects=True,
    )
    print("Login status:", resp.status_code)
    # load lab page
    r = client.get("/lab/1")
    print("/lab/1 status:", r.status_code)
    # get topology
    t = client.get("/api/lab/1/topology")
    print("/api/lab/1/topology status:", t.status_code)
    topo = t.get_json()
    print(
        "topo nodes:", len(topo.get("nodes", [])), "edges:", len(topo.get("edges", []))
    )
    # add a small topology link between R1 and R2
    edges = [
        {
            "from": "R1",
            "to": "R2",
            "label": "smoke",
            "cost": 4,
            "src_if": "G0/0",
            "dst_if": "G0/0",
        }
    ]
    s = client.post("/api/lab/1/topology", json={"edges": edges, "jitter_seed": 12345})
    print("POST topology status:", s.status_code, s.get_json())
    # get device config for R1
    g = client.get("/api/lab/1/device/R1/config")
    print("GET R1 config status:", g.status_code)
    # set R2 interface to a target IP
    set_r = client.post(
        "/api/lab/1/device/R2/config",
        json={"interfaces": [{"name": "G0/0", "ip": "203.0.113.99"}]},
    )
    print("SET R2 config status:", set_r.status_code)
    # traceroute from R1 to R2 IP
    tr = client.post(
        "/api/lab/1/device/R1/command", json={"command": "traceroute 203.0.113.99"}
    )
    print("Traceroute status:", tr.status_code)
    print(tr.get_json().get("output"))
    # ping test
    p = client.post(
        "/api/lab/1/device/R1/command", json={"command": "ping 203.0.113.99"}
    )
    print("Ping output:", p.get_json().get("output"))
