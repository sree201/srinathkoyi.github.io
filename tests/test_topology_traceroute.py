import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json

from sqlalchemy import select

from app import Lab, LabDevice, app, db


def login_client(client, username="testuser2", password="password"):
    with app.app_context():
        u = app.config.get("TEST_USER")
        # create user if not exists
        from app import User

        user = db.session.scalars(select(User).filter_by(username=username)).first()
        if not user:
            user = User(username=username, email=f"{username}@example.com")
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
    resp = client.post(
        "/login",
        data={"username": username, "password": password},
        follow_redirects=True,
    )
    return resp


def test_save_and_load_topology_edge_metadata():
    client = app.test_client()
    login_client(client)
    # Create a simple edge payload and save it
    edges = [
        {
            "from": "R1",
            "to": "R2",
            "label": "R1-R2",
            "cost": 5,
            "src_if": "G0/0",
            "dst_if": "G0/0",
        }
    ]
    r = client.post("/api/lab/1/topology", json={"edges": edges})
    assert r.status_code == 200
    data = r.get_json()
    assert data.get("success") is True
    # Reload topology and verify metadata present
    r2 = client.get("/api/lab/1/topology")
    assert r2.status_code == 200
    payload = r2.get_json()
    found = any(
        (
            e.get("from") == "R1"
            and e.get("to") == "R2"
            and (
                e.get("cost") == 5
                or e.get("label") == "R1-R2"
                or e.get("src_if") == "G0/0"
            )
        )
        for e in payload.get("edges", [])
    )
    assert found, "Saved edge metadata not found in GET topology"


def test_ping_traceroute_behavior_with_costs():
    client = app.test_client()
    login_client(client)
    # ensure target IP on R2 and link exists
    with app.app_context():
        lab = db.session.get(Lab, 1)
        devices = {d.device_name: d for d in lab.devices}
        assert "R1" in devices and "R2" in devices
        r2 = devices["R2"]
        r2.interfaces = json.dumps([{"name": "G0/0", "ip": "203.0.113.5/32"}])
        lab.lab_config = json.dumps(
            {
                "links": [
                    {
                        "from": "R1",
                        "to": "R2",
                        "cost": 7,
                        "src_if": "G0/0",
                        "dst_if": "G0/0",
                    }
                ]
            }
        )
        db.session.commit()
    # ping should succeed
    r = client.post(
        "/api/lab/1/device/R1/command", json={"command": "ping 203.0.113.5"}
    )
    assert r.status_code == 200
    out = r.get_json().get("output", "")
    assert "Success rate is 100 percent" in out
    # traceroute should show cost-based latency (center number equals cost)
    r2 = client.post(
        "/api/lab/1/device/R1/command", json={"command": "traceroute 203.0.113.5"}
    )
    assert r2.status_code == 200
    out2 = r2.get_json().get("output", "")
    # header should reference the target, and hops should show device names
    assert "Tracing the route to 203.0.113.5" in out2
    assert "R2" in out2
    # expect the hop line for R2 contains '7 msec' as the middle value
    assert "7 msec" in out2


def test_ping_unreachable_when_no_path():
    client = app.test_client()
    login_client(client)
    # create an isolated device with the target IP (no links to it)
    with app.app_context():
        lab = db.session.get(Lab, 1)
        devices = {d.device_name: d for d in lab.devices}
        # clear explicit links to avoid accidental connections
        lab.lab_config = json.dumps({"links": []})
        # create isolated device (type not 'pc/router/switch' so auto-topology won't connect it)
        isolated = LabDevice(
            lab_id=lab.id,
            device_name="ISOLATED",
            device_type="Isolated",
            vendor="Generic",
            model="Virtual",
        )
        isolated.interfaces = json.dumps([{"name": "eth0", "ip": "198.51.100.5/32"}])
        db.session.add(isolated)
        db.session.commit()
    # ping should now be unreachable
    r = client.post(
        "/api/lab/1/device/R1/command", json={"command": "ping 198.51.100.5"}
    )
    assert r.status_code == 200
    out = r.get_json().get("output", "")
    assert "Destination host unreachable" in out or "Success rate is 0 percent" in out


def test_multi_hop_latencies_and_jitter():
    client = app.test_client()
    login_client(client)
    with app.app_context():
        lab = db.session.get(Lab, 1)
        # ensure devices exist or create R3
        devs = {d.device_name: d for d in lab.devices}
        if "R3" not in devs:
            r3 = LabDevice(
                lab_id=lab.id,
                device_name="R3",
                device_type="Router",
                vendor="Generic",
                model="v1",
            )
            db.session.add(r3)
            db.session.commit()
        else:
            r3 = devs["R3"]
        # set a multi-hop: R1 - R2 (cost 3), R2 - R3 (cost 5 + jitter 2). Use deterministic seed.
        seed = 4242
        lab.lab_config = json.dumps(
            {
                "links": [
                    {
                        "from": "R1",
                        "to": "R2",
                        "cost": 3,
                        "src_if": "G0/0",
                        "dst_if": "G0/0",
                    },
                    {
                        "from": "R2",
                        "to": "R3",
                        "cost": 5,
                        "jitter": 2,
                        "src_if": "G0/0",
                        "dst_if": "G0/1",
                    },
                ],
                "jitter_seed": seed,
            }
        )
        # set target IP on R3
        r3.interfaces = json.dumps([{"name": "G0/1", "ip": "198.51.100.9"}])
        db.session.commit()
    # traceroute from R1 to the R3 IP
    tr = client.post(
        "/api/lab/1/device/R1/command", json={"command": "traceroute 198.51.100.9"}
    )
    assert tr.status_code == 200
    out = tr.get_json().get("output", "")
    # should contain R2 and R3 lines
    assert "R2" in out and "R3" in out
    # R2 hop should have '3 msec' as mid value (deterministic due to seed)
    import random
    import re

    m2 = re.search(r"\n\s*2\s+R2.*?(\d+) msec (\d+) msec (\d+) msec", out, re.S)
    assert m2, f"Could not find hop line for R2 in output:\n{out}"
    mid_r2 = int(m2.group(2))
    assert mid_r2 == 3, f"R2 mid latency expected 3 but got {mid_r2}"
    # R3 hop deterministic mid value
    m3 = re.search(r"\n\s*3\s+R3.*?(\d+) msec (\d+) msec (\d+) msec", out, re.S)
    assert m3, f"Could not find hop line for R3 in output:\n{out}"
    mid = int(m3.group(2))
    # compute expected midpoint using same deterministic sampling
    seed = 4242
    rnd = random.Random(seed + 2)  # hop index 2
    expected_j = rnd.randint(0, 2)
    expected_mid = 5 + expected_j
    assert (
        mid == expected_mid
    ), f"mid latency {mid} does not match expected {expected_mid} (jitter {expected_j})"


def test_ip_normalization_to_cidr():
    client = app.test_client()
    login_client(client)
    payload = {"interfaces": [{"name": "Gx0", "ip": "10.10.1.5"}]}
    r = client.post("/api/lab/1/device/R1/config", json=payload)
    assert r.status_code == 200
    # GET back config and verify normalized ip (should be /32) and have address/network fields
    g = client.get("/api/lab/1/device/R1/config")
    assert g.status_code == 200
    data = g.get_json()
    interfaces = data.get("interfaces", [])
    found = False
    for it in interfaces:
        if it.get("name") == "Gx0":
            assert it.get("ip", "").endswith("/32")
            assert "address" in it and it["address"] == "10.10.1.5"
            assert "network" in it and "/32" in it["network"]
            found = True
    assert found


def test_jitter_seed_determinism():
    client = app.test_client()
    login_client(client)
    # set R2 ip and link with jitter
    with app.app_context():
        lab = db.session.get(Lab, 1)
        devices = {d.device_name: d for d in lab.devices}
        r2 = devices["R2"]
        r2.interfaces = json.dumps([{"name": "G0/0", "ip": "203.0.113.55/32"}])
        lab.lab_config = json.dumps(
            {
                "links": [{"from": "R1", "to": "R2", "cost": 5, "jitter": 3}],
                "jitter_seed": 777,
            }
        )
        db.session.commit()
    t1 = (
        client.post(
            "/api/lab/1/device/R1/command", json={"command": "traceroute 203.0.113.55"}
        )
        .get_json()
        .get("output")
    )
    t2 = (
        client.post(
            "/api/lab/1/device/R1/command", json={"command": "traceroute 203.0.113.55"}
        )
        .get_json()
        .get("output")
    )
    assert t1 == t2
    # change seed and expect a different output
    with app.app_context():
        lab = db.session.get(Lab, 1)
        cfg = json.loads(lab.lab_config or "{}")
        cfg["jitter_seed"] = 888
        lab.lab_config = json.dumps(cfg)
        db.session.commit()
    t3 = (
        client.post(
            "/api/lab/1/device/R1/command", json={"command": "traceroute 203.0.113.55"}
        )
        .get_json()
        .get("output")
    )
    assert t3 != t1
