import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import json

from app import Lab, app, db, simulate_network_command

with app.app_context():
    lab = db.session.get(Lab, 1)
    if not lab:
        print("Lab 1 not found")
    else:
        devs = {d.device_name: d for d in lab.devices}
        print("devices:", list(devs.keys()))
        if "R1" in devs and "R2" in devs:
            lab.lab_config = json.dumps(
                {
                    "links": [
                        {
                            "from": "R1",
                            "to": "R2",
                            "cost": 5,
                            "src_if": "G0/0",
                            "dst_if": "G0/0",
                        }
                    ]
                }
            )
            r2 = devs["R2"]
            r2.interfaces = json.dumps([{"name": "G0/0", "ip": "8.8.8.8/32"}])
            db.session.commit()
            # debug: show parsed links and target IPs
            import json
            import re

            cfg = json.loads(lab.lab_config or "{}")
            links = cfg.get("links", [])
            print("links in lab_config:", links)

            def extract_ips(dev):
                ips = set()
                if dev.interfaces:
                    try:
                        j = json.loads(dev.interfaces)

                        def _walk(obj):
                            if isinstance(obj, dict):
                                for v in obj.values():
                                    _walk(v)
                            elif isinstance(obj, list):
                                for item in obj:
                                    _walk(item)
                            elif isinstance(obj, str):
                                for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", obj):
                                    ips.add(m)

                        _walk(j)
                    except Exception:
                        pass
                if dev.initial_config:
                    for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", dev.initial_config):
                        ips.add(m)
                return ips

            for name, d in devs.items():
                print(name, "ips:", extract_ips(d))
            # build adjacency like simulate_network_command does
            import collections

            adj = collections.defaultdict(list)
            if links:
                for link in links:
                    if isinstance(link, (list, tuple)) and len(link) >= 2:
                        a, b = link[0], link[1]
                        adj[a].append(b)
                        adj[b].append(a)
                    elif isinstance(link, dict):
                        a, b = link.get("from"), link.get("to")
                        if a and b:
                            adj[a].append(b)
                            adj[b].append(a)
            print("adjacency:", dict(adj))
            # compute targets
            target = "8.8.8.8"

            def _extract_ips_local(dev):
                import re

                ips = set()
                if dev.interfaces:
                    try:
                        j = json.loads(dev.interfaces)

                        def _walk(obj):
                            if isinstance(obj, dict):
                                for v in obj.values():
                                    _walk(v)
                            elif isinstance(obj, list):
                                for item in obj:
                                    _walk(item)
                            elif isinstance(obj, str):
                                for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", obj):
                                    ips.add(m)

                        _walk(j)
                    except Exception:
                        pass
                if dev.initial_config:
                    for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", dev.initial_config):
                        ips.add(m)
                return ips

            targets = [name for name, d in devs.items() if target in _extract_ips_local(d)]
            print("targets found for", target, ":", targets)

            # BFS
            src = "R1"
            from collections import deque

            visited = set([src])
            q = deque([[src]])
            path = None
            while q and not path:
                p = q.popleft()
                node = p[-1]
                if node in targets:
                    path = p
                    break
                for nb in adj.get(node, []):
                    if nb not in visited:
                        visited.add(nb)
                        q.append(p + [nb])
            print("bfs path:", path)

            out = simulate_network_command(devs["R1"], "traceroute 8.8.8.8")
            print("\nTraceroute output:\n", out)
        else:
            print("R1 or R2 missing in lab 1")
