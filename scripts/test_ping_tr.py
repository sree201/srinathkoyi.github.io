import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from app import Lab, app, db, simulate_network_command

with app.app_context():
    lab = db.session.get(Lab, 1)
    devs = {d.device_name: d for d in lab.devices}
    if "R1" in devs:
        print("Ping output:\n", simulate_network_command(devs["R1"], "ping 8.8.8.8"))
        print(
            "Traceroute output:\n",
            simulate_network_command(devs["R1"], "traceroute 8.8.8.8"),
        )
    else:
        print("R1 missing")
