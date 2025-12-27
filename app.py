"""
CCNA Practice Platform - Main Flask Application
A platform for CCNA networking practice with Cisco and Arista devices
"""

import os
import secrets
from datetime import datetime

from dotenv import load_dotenv
from flask import (
    Flask,
    abort,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import (
    LoginManager,
    UserMixin,
    current_user,
    login_required,
    login_user,
    logout_user,
)
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func, not_, or_, select
from werkzeug.security import check_password_hash, generate_password_hash

# Load environment variables from .env (if present)
load_dotenv()

# Simple in-memory DNS store for lab simulations: { lab_id: { hostname: html_response } }
dns_store = {}

# Device authentication state: { user_id: { lab_id: { device_name: authenticated } } }
device_auth_state = {}


app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", secrets.token_hex(16))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///ccna_labs.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "info"


# Database Models
class User(UserMixin, db.Model):
    """User model for authentication"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    labs_completed = db.Column(db.Integer, default=0)
    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    user_labs = db.relationship("UserLab", backref="user", lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


class Lab(db.Model):
    """Lab model for practice scenarios"""

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    difficulty = db.Column(db.String(20), default="Beginner")  # Beginner, Intermediate, Advanced
    category = db.Column(db.String(100))  # Routing, Switching, Security, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

    # Lab configuration (JSON stored as string or use JSON field if available)
    lab_config = db.Column(db.Text)  # JSON string with device configurations

    # New fields in Lab model:
    lab_number = db.Column(db.Integer, default=0)
    full_description = db.Column(db.Text)
    requires_environment = db.Column(db.Boolean, default=False)

    # Relationships
    user_labs = db.relationship("UserLab", backref="lab", lazy=True)
    devices = db.relationship("LabDevice", backref="lab", lazy=True, cascade="all, delete-orphan")


class LabDevice(db.Model):
    """Device model for lab equipment (Cisco/Arista)"""

    id = db.Column(db.Integer, primary_key=True)
    lab_id = db.Column(db.Integer, db.ForeignKey("lab.id"), nullable=False)
    device_name = db.Column(db.String(100), nullable=False)
    device_type = db.Column(db.String(50), nullable=False)  # Router, Switch
    vendor = db.Column(db.String(50), nullable=False)  # Cisco, Arista
    model = db.Column(db.String(100))  # e.g., Cisco ISR4331, Arista DCS-7050SX
    initial_config = db.Column(db.Text)  # Initial configuration
    interfaces = db.Column(db.Text)  # JSON string with interface configurations


class UserLab(db.Model):
    """User lab progress tracking"""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    lab_id = db.Column(db.Integer, db.ForeignKey("lab.id"), nullable=False)
    status = db.Column(db.String(20), default="Not Started")  # Not Started, In Progress, Completed
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    score = db.Column(db.Integer)  # 0-100
    current_config = db.Column(db.Text)  # Current device configurations (JSON)


@login_manager.user_loader
def load_user(user_id):
    # Use session.get to avoid SQLAlchemy Query.get deprecation warnings
    try:
        return db.session.get(User, int(user_id))
    except Exception:
        return None


# Routes
@app.route("/")
def index():
    """Landing page similar to devopsxlabs"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        if db.session.scalars(select(User).filter_by(username=username)).first():
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        if db.session.scalars(select(User).filter_by(email=email)).first():
            flash("Email already registered", "error")
            return redirect(url_for("register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = bool(request.form.get("remember"))

        user = db.session.scalars(select(User).filter_by(username=username)).first()

        if user and user.check_password(password):
            login_user(user, remember=remember)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("dashboard"))
        else:
            flash("Invalid username or password", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    """User logout"""
    logout_user()
    flash("You have been logged out", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    """User dashboard"""
    # Get user's labs
    user_labs = db.session.scalars(select(UserLab).filter_by(user_id=current_user.id)).all()

    # Get all available labs
    available_labs = db.session.scalars(select(Lab).filter_by(is_active=True)).all()

    # Get stats
    completed_labs = len([ul for ul in user_labs if ul.status == "Completed"])

    return render_template(
        "dashboard.html",
        user_labs=user_labs,
        available_labs=available_labs,
        completed_labs=completed_labs,
    )


@app.route("/labs")
@login_required
def labs():
    """List all available labs"""
    labs_list = db.session.scalars(select(Lab).filter_by(is_active=True)).all()
    return render_template("labs.html", labs=labs_list)


@app.route("/ai-lab-coach")
def ai_lab_coach():
    """AI Lab Coach landing page"""
    return render_template("ai_lab_coach.html")


@app.route("/build-lab", methods=["GET", "POST"])
@login_required
def build_lab():
    """Personalized lab builder - topic selection"""
    if request.method == "POST":
        topic = request.form.get("topic")
        if topic:
            return redirect(url_for("select_subtopics", topic=topic))

    return render_template("build_lab.html")


@app.route("/build-lab/<topic>/subtopics", methods=["GET", "POST"])
@login_required
def select_subtopics(topic):
    """Sub-topic selection page"""
    if request.method == "POST":
        subtopics = request.form.getlist("subtopics")
        difficulty = request.form.get("difficulty")
        if subtopics and difficulty:
            session["lab_preferences"] = {"topic": topic, "subtopics": subtopics, "difficulty": difficulty}
            return redirect(url_for("lab_list", topic=topic, difficulty=difficulty))

    # Define sub-topics for each topic
    subtopics_map = {
        "networking": [
            "OSI Model & TCP/IP",
            "DNS",
            "HTTP/HTTPS",
            "Subnetting & CIDR",
            "Firewalls & Security Groups",
            "Load Balancing",
            "VPNs & Tunneling",
            "BGP & Routing Protocols",
            "VPC & Cloud Networking",
            "Network Troubleshooting Tools",
            "Software Defined Networking (SDN)",
        ],
        "linux": [
            "Command Line Basics",
            "File System & Permissions",
            "Shell Scripting (Bash)",
            "Process Management",
            "Systemd & Service Management",
            "User & Group Management",
            "Linux Networking Tools (ip, ss)",
            "Package Management (apt/yum)",
            "Linux Security & Hardening",
            "I/O Redirection & Pipelines",
            "Kernel Basics",
        ],  # type: ignore
        "docker": [
            "Image Creation & Dockerfiles",
            "Docker Swarm",
            "Docker Registries",
            "Health Checks & Monitoring",
            "Docker Networking",
            "Container Security",
            "Multi-stage Builds",
            "Docker Compose",
            "Docker Volumes & Persistence",
            "Docker Engine Internals",
        ],
        "kubernetes": [
            "Pods & Containers",
            "Deployments & ReplicaSets",
            "Services & Networking",
            "ConfigMaps & Secrets",
            "Persistent Volumes",
            "Ingress Controllers",
            "Helm Charts",
            "Kubernetes Networking",
            "RBAC & Security",
            "Monitoring & Logging",
        ],
    }

    subtopics = subtopics_map.get(topic.lower(), [])
    return render_template("select_subtopics.html", topic=topic, subtopics=subtopics)


@app.route("/build-lab/<topic>/labs", methods=["GET"])
@login_required
def lab_list(topic):
    """Lab listing page with selected topic and difficulty"""
    difficulty = request.args.get("difficulty", "Beginner")

    # Get labs based on topic and difficulty
    labs_query = select(Lab).filter_by(is_active=True)

    # Filter by difficulty if provided
    if difficulty:
        labs_query = labs_query.filter_by(difficulty=difficulty)

    # Filter by category/topic (simplified - you may want to add topic field to Lab model)
    labs_list = db.session.scalars(labs_query).all()

    # For now, we'll show all labs and let the frontend filter
    return render_template("lab_list.html", topic=topic, difficulty=difficulty, labs=labs_list)


@app.route("/lab/<int:lab_id>")
@login_required
def lab_detail(lab_id):
    """Lab detail page with lab theory, practice, and test sections"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)

    # Get or create user lab session
    user_lab = db.session.scalars(select(UserLab).filter_by(user_id=current_user.id, lab_id=lab_id)).first()
    if not user_lab:
        user_lab = UserLab(
            user_id=current_user.id,
            lab_id=lab_id,
            status="In Progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(user_lab)
        db.session.commit()

    # Get devices for this lab, excluding ISOLATED devices and R3 Generic v1
    devices = db.session.scalars(
        select(LabDevice)
        .filter_by(lab_id=lab_id)
        .filter(LabDevice.device_type != "Isolated")
        .filter(not_(LabDevice.device_name.like("ISOLATED%")))
        .filter(not_((LabDevice.device_name == "R3") & (LabDevice.vendor == "Generic") & (LabDevice.model == "v1")))
    ).all()

    return render_template("lab_detail.html", lab=lab, devices=devices, user_lab=user_lab)


# THIS ROUTE SHOULD ALSO EXIST:
@app.route("/lab/<int:lab_id>/start")
@login_required
def lab_start(lab_id):
    """Start lab environment with terminal interface"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    # Get or create user lab session
    user_lab = db.session.scalars(select(UserLab).filter_by(user_id=current_user.id, lab_id=lab_id)).first()
    if not user_lab:
        user_lab = UserLab(
            user_id=current_user.id,
            lab_id=lab_id,
            status="In Progress",
            started_at=datetime.utcnow(),
        )
        db.session.add(user_lab)
        db.session.commit()

    # Get devices for this lab
    devices = db.session.scalars(
        select(LabDevice)
        .filter_by(lab_id=lab_id)
        .filter(LabDevice.device_type != "Isolated")
        .filter(not_(LabDevice.device_name.like("ISOLATED%")))
    ).all()

    return render_template("lab_terminal.html", lab=lab, devices=devices, user_lab=user_lab)


@app.route("/api/lab/<int:lab_id>/devices")
@login_required
def list_devices(lab_id):
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    devices = db.session.scalars(
        select(LabDevice)
        .filter_by(lab_id=lab_id)
        .filter(LabDevice.device_type != "Isolated")
        .filter(not_(LabDevice.device_name.like("ISOLATED%")))
    ).all()
    return jsonify(
        {
            "devices": [
                {
                    "name": d.device_name,
                    "type": d.device_type,
                    "vendor": d.vendor,
                    "model": d.model,
                }
                for d in devices
            ]
        }
    )


@app.route("/api/lab/<int:lab_id>/topology")
@login_required
def lab_topology(lab_id):
    """Return a simple topology (nodes+edges) for visualization."""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    devices = db.session.scalars(select(LabDevice).filter_by(lab_id=lab_id)).all()

    nodes = []
    edges = []

    # Build nodes
    for d in devices:
        group = (d.device_type or "Unknown").lower()
        nodes.append(
            {
                "id": d.device_name,
                "label": d.device_name,
                "group": group,
                "title": f"{d.vendor} {d.model}",
            }
        )

    # Try to read explicit links from lab.lab_config if present
    import json

    links = []
    try:
        cfg = json.loads(lab.lab_config or "{}")
        links = cfg.get("links", []) or []
    except Exception:
        links = []

    device_names = [d.device_name for d in devices]

    positions = None
    if links:
        # links may be plain pairs or dicts with metadata
        for link in links:
            if isinstance(link, dict):
                a = link.get("from")
                b = link.get("to")
                if a in device_names and b in device_names:
                    edge = {"from": a, "to": b}
                    # include optional metadata if present
                    for key in ("label", "cost", "src_if", "dst_if", "jitter"):
                        if key in link:
                            edge[key] = link[key]
                    edges.append(edge)
            elif (
                isinstance(link, (list, tuple))
                and len(link) >= 2
                and link[0] in device_names
                and link[1] in device_names
            ):
                edges.append({"from": link[0], "to": link[1]})
        # try read positions and jitter_seed too
        try:
            cfg = json.loads(lab.lab_config or "{}")
            if "positions" in cfg:
                positions = cfg.get("positions")
            # include jitter seed when present
            if "jitter_seed" in cfg:
                jitter_seed = cfg.get("jitter_seed")
                # include into positions output for client visibility
                if not positions:
                    positions = {}
                positions["_jitter_seed"] = jitter_seed
        except Exception:
            positions = None
    else:
        # Auto generate a simple topology:
        routers = [d.device_name for d in devices if d.device_type and d.device_type.lower() == "router"]
        switches = [d.device_name for d in devices if d.device_type and d.device_type.lower() == "switch"]
        pcs = [d.device_name for d in devices if d.device_type and d.device_type.lower() == "pc"]

        # Connect routers in a chain (if >1)
        for i in range(len(routers) - 1):
            edges.append({"from": routers[i], "to": routers[i + 1]})

        # Connect each switch to the first router (or chain them if no router)
        if routers:
            main_router = routers[0]
            for sw in switches:
                edges.append({"from": sw, "to": main_router})
        else:
            # connect switches in a chain
            for i in range(len(switches) - 1):
                edges.append({"from": switches[i], "to": switches[i + 1]})

        # Connect PCs to first switch if present, else to first router
        if switches:
            main_switch = switches[0]
            for pc in pcs:
                edges.append({"from": pc, "to": main_switch})
        elif routers:
            main_router = routers[0]
            for pc in pcs:
                edges.append({"from": pc, "to": main_router})

    return jsonify({"nodes": nodes, "edges": edges, "positions": positions})


@app.route("/api/lab/<int:lab_id>/topology", methods=["POST"])
@login_required
def save_lab_topology(lab_id):
    """Persist topology links into lab.lab_config.links"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    data = request.get_json() or {}
    edges = data.get("edges")
    if edges is None or not isinstance(edges, list):
        return jsonify({"success": False, "error": "edges list required"}), 400

    # validate and convert to link structures with optional metadata
    devices = [d.device_name for d in db.session.scalars(select(LabDevice).filter_by(lab_id=lab_id)).all()]
    cleaned = []
    for e in edges:
        if not isinstance(e, dict):
            continue
        a = e.get("from")
        b = e.get("to")
        if a in devices and b in devices:
            link = {"from": a, "to": b}
            for key in ("label", "cost", "src_if", "dst_if"):
                if key in e:
                    link[key] = e.get(key)
            cleaned.append(link)

    # update lab_config JSON
    import json

    try:
        cfg = json.loads(lab.lab_config or "{}")
    except Exception:
        cfg = {}
    cfg["links"] = cleaned
    # optionally accept node positions
    positions = data.get("positions")
    if positions and isinstance(positions, dict):
        cfg["positions"] = positions
    # optionally accept jitter seed for deterministic jitter sampling
    seed_val = data.get("jitter_seed") if data.get("jitter_seed") is not None else data.get("seed")
    if seed_val is not None:
        cfg["jitter_seed"] = seed_val
    lab.lab_config = json.dumps(cfg)
    db.session.commit()
    return jsonify(
        {
            "success": True,
            "links": cleaned,
            "positions": cfg.get("positions"),
            "jitter_seed": cfg.get("jitter_seed"),
        }
    )


@app.route("/api/lab/<int:lab_id>/device/<device_name>/command", methods=["POST"])
@login_required
def execute_command(lab_id, device_name):
    """Execute command on network device (simulated)"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    device = db.session.query(LabDevice).filter_by(lab_id=lab_id, device_name=device_name).first()
    if device is None:
        abort(404)

    data = request.get_json()
    command = data.get("command", "")
    password = data.get("password", "")

    # Initialize auth state for this user/lab/device
    if current_user.id not in device_auth_state:
        device_auth_state[current_user.id] = {}
    if lab_id not in device_auth_state[current_user.id]:
        device_auth_state[current_user.id][lab_id] = {}

    is_authenticated = device_auth_state[current_user.id][lab_id].get(device_name, False)

    # Check if device requires authentication (routers and switches)
    requires_auth = device.device_type.lower() in ["router", "switch"]

    # Handle login commands
    command_lower = command.strip().lower()
    if requires_auth and not is_authenticated:
        if command_lower in ["enable", "en"]:
            # Check password (default: "cisco" for demo)
            if password == "cisco" or password == "":
                device_auth_state[current_user.id][lab_id][device_name] = True
                return jsonify({"success": True, "output": "", "device": device_name, "authenticated": True})
            else:
                return jsonify(
                    {
                        "success": False,
                        "output": "% Access denied",
                        "device": device_name,
                        "authenticated": False,
                        "requires_password": True,
                    }
                )
        elif command_lower == "":
            # Empty command - show prompt
            return jsonify(
                {
                    "success": True,
                    "output": "",
                    "device": device_name,
                    "authenticated": False,
                    "prompt": f"{device_name}>",
                }
            )
        else:
            # Allow certain informational/diagnostic commands without enable
            if command_lower.startswith(("ping", "traceroute")):
                result = simulate_network_command(device, command)
                return jsonify(
                    {
                        "success": True,
                        "output": result,
                        "device": device_name,
                        "authenticated": False,
                    }
                )
            # Command requires authentication
            return jsonify(
                {
                    "success": False,
                    "output": "% Access denied. Use 'enable' to enter privileged mode.",
                    "device": device_name,
                    "authenticated": False,
                }
            )

    # Simulate command execution
    # In a real implementation, this would interface with network emulation software
    result = simulate_network_command(device, command)

    # Handle disable command
    if command_lower in ["disable", "dis"] and is_authenticated:
        device_auth_state[current_user.id][lab_id][device_name] = False

    return jsonify(
        {
            "success": True,
            "output": result,
            "device": device_name,
            "authenticated": is_authenticated,
        }
    )


# Device configuration endpoints (interfaces/hostname)
@app.route("/api/lab/<int:lab_id>/device/<device_name>/config", methods=["GET"])
@login_required
def get_device_config(lab_id, device_name):
    """Return device config (interfaces JSON and hostname)"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    device = db.session.query(LabDevice).filter_by(lab_id=lab_id, device_name=device_name).first()
    if device is None:
        abort(404)
    # parse interfaces JSON
    import json

    try:
        interfaces = json.loads(device.interfaces) if device.interfaces else []
    except Exception:
        interfaces = []
    # extract hostname from initial_config if present
    hostname = device.device_name
    if device.initial_config:
        firstline = device.initial_config.strip().splitlines()[0].strip()
        if firstline.lower().startswith("hostname"):
            parts = firstline.split()
            if len(parts) >= 2:
                hostname = parts[1]
    return jsonify({"device": device.device_name, "hostname": hostname, "interfaces": interfaces})


@app.route("/api/lab/<int:lab_id>/device/<device_name>/config", methods=["POST"])
@login_required
def set_device_config(lab_id, device_name):
    """Persist device config (interfaces list and hostname)"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    device = db.session.query(LabDevice).filter_by(lab_id=lab_id, device_name=device_name).first()
    if device is None:
        abort(404)
    data = request.get_json() or {}
    interfaces = data.get("interfaces")
    hostname = data.get("hostname")
    import json

    if interfaces is not None:
        # interfaces must be a list of objects with at least a name and optional ip
        if not isinstance(interfaces, list):
            return (
                jsonify({"success": False, "error": "interfaces must be a list"}),
                400,
            )
        validated = []
        errors = []
        import ipaddress

        for idx, it in enumerate(interfaces):
            if not isinstance(it, dict):
                errors.append(f"interface at index {idx} must be an object")
                continue
            name = (it.get("name") or "").strip()
            ip = (it.get("ip") or "").strip()
            if not name:
                errors.append(f"interface at index {idx} missing name")
            if ip:
                # accept either plain IPv4 address or IPv4 with CIDR (/0-32)
                try:
                    if "/" in ip:
                        ip_obj = ipaddress.ip_interface(ip)
                    else:
                        # normalize to a host /32 interface
                        ip_obj = ipaddress.ip_interface(ip + "/32")
                    ip_norm = str(ip_obj)
                    ip_addr = str(ip_obj.ip)
                    ip_net = str(ip_obj.network)
                except Exception:
                    errors.append(f'interface "{name or idx}" has invalid ip "{ip}"')
                    ip_norm = ip
                    ip_addr = ""
                    ip_net = ""
            else:
                ip_norm = ""
                ip_addr = ""
                ip_net = ""
            validated.append({"name": name, "ip": ip_norm, "address": ip_addr, "network": ip_net})
        if errors:
            return jsonify({"success": False, "errors": errors}), 400
        device.interfaces = json.dumps(validated)
    if hostname:
        # update initial_config hostname line (replace existing or prepend)
        lines = device.initial_config.splitlines() if device.initial_config else []
        if lines and lines[0].lower().startswith("hostname"):
            lines[0] = f"hostname {hostname}"
        else:
            lines.insert(0, f"hostname {hostname}")
        device.initial_config = "\n".join(lines)
    db.session.commit()
    return jsonify({"success": True, "device": device.device_name, "hostname": hostname or None})


# --- PC browser and DNS simulation endpoints ---
@app.route("/lab/<int:lab_id>/device/<device_name>/browser")
@login_required
def pc_browser(lab_id, device_name):
    """Render a simple PC browser UI for a PC device"""
    lab = db.session.get(Lab, lab_id)
    if lab is None:
        abort(404)
    device = db.session.query(LabDevice).filter_by(lab_id=lab_id, device_name=device_name).first()
    if device is None:
        abort(404)
    if device.device_type.lower() != "pc":
        flash("Browser view is only available for PC devices", "error")
        return redirect(url_for("lab_detail", lab_id=lab_id))

    # Ensure DNS store exists for this lab
    dns_store.setdefault(lab_id, {})

    return render_template("pc_browser.html", lab=lab, device=device)


@app.route("/api/lab/<int:lab_id>/dns", methods=["POST"])
@login_required
def add_dns_record(lab_id):
    """Add a DNS mapping for a lab (hostname -> simulated HTML/text)."""
    data = request.get_json() or {}
    host = data.get("host")
    response = data.get("response", "")
    if not host:
        return jsonify({"success": False, "error": "host required"}), 400
    dns_store.setdefault(lab_id, {})[host] = response
    return jsonify({"success": True})


@app.route("/api/lab/<int:lab_id>/pc/<device_name>/browse", methods=["POST"])
@login_required
def pc_browse(lab_id, device_name):
    """Simulated browser fetch: resolve host via dns_store and return the stored HTML/text."""
    data = request.get_json() or {}
    host = data.get("host")
    if not host:
        return jsonify({"success": False, "error": "host required"}), 400

    records = dns_store.get(lab_id, {})
    if host in records:
        return jsonify({"success": True, "content": records[host]})
    else:
        return (
            jsonify(
                {
                    "success": False,
                    "error": f"Host '{host}' not found (use /api/lab/{lab_id}/dns to add)",
                }
            ),
            404,
        )


def simulate_network_command(device, command):
    """Simulate network device command execution with enhanced command support"""
    command_lower = command.strip().lower()
    vendor = device.vendor.lower()

    # Handle vendor-specific commands
    if vendor == "arista":
        return simulate_arista_command(device, command)

    # Cisco IOS Commands
    # Enable command - handled in execute_command route with authentication
    if command_lower in ["enable", "en"]:
        return ""  # Authentication handled in route

    # Disable command - handled in execute_command route
    elif command_lower in ["disable", "dis"]:
        return ""  # State change handled in route

    # Show commands
    elif command_lower.startswith("show") or command_lower.startswith("sh"):
        return handle_show_command(device, command_lower)

    # Configure terminal
    elif (
        command_lower.startswith("configure terminal")
        or command_lower.startswith("conf t")
        or command_lower == "config"
    ):
        return "Enter configuration commands, one per line. End with CNTL/Z."

    # Configuration mode commands
    elif command_lower.startswith("interface") or command_lower.startswith("int "):
        name = command.split()[-1] if len(command.split()) > 1 else "interface"
        return f"Entering interface configuration mode for {name}"

    elif command_lower.startswith("router ") or command_lower.startswith("router-"):
        protocol = command.split()[1] if len(command.split()) > 1 else "protocol"
        return f"Entering router configuration mode for {protocol}"

    elif command_lower.startswith("vlan "):
        vlan_id = command.split()[1] if len(command.split()) > 1 else "vlan"
        return f"Entering VLAN configuration mode for VLAN {vlan_id}"

    elif command_lower.startswith("ip address") or command_lower.startswith("ip addr"):
        return "IP address configured"

    elif command_lower.startswith("ip route"):
        return "Static route added"

    elif command_lower == "no shutdown" or command_lower == "no shut":
        return ""

    elif command_lower == "shutdown" or command_lower == "shut":
        return ""

    elif command_lower.startswith("switchport mode"):
        return ""

    elif command_lower.startswith("switchport access vlan"):
        return ""

    elif command_lower.startswith("switchport trunk allowed vlan"):
        return ""

    elif command_lower.startswith("hostname"):
        new_hostname = command.split()[1] if len(command.split()) > 1 else "router"
        return f"Hostname changed to {new_hostname}"

    elif command_lower.startswith("router ospf") or command_lower.startswith("router-ospf"):
        return "Entering router OSPF configuration mode"

    elif command_lower.startswith("router eigrp"):
        return "Entering router EIGRP configuration mode"

    elif command_lower.startswith("network "):
        return "Network added to routing protocol"

    elif command_lower.startswith("access-list"):
        return "Access list entry added"

    elif command_lower.startswith("ip access-group"):
        return "Access group applied to interface"

    # Exit commands
    elif command_lower in ["exit", "end", "quit"]:
        return ""

    # Help command
    elif command_lower == "?":
        return """Exec commands:
  <1-99>        Session number to resume
  enable        Turn on privileged commands
  configure     Enter configuration mode
  connect       Open a terminal connection
  copy          Copy from one file to another
  debug         Debugging functions (see also 'undebug')
  disable       Turn off privileged commands
  disconnect    Disconnect an existing network connection
  exit          Exit EXEC
  ping          Send echo messages
  show          Show running system information
  ssh           Open a secure shell client connection
  telnet        Open a telnet connection
  terminal      Set terminal line parameters
  traceroute    Trace route to destination
  write         Write to startup config
  reload        Reload system
"""

    # Ping command (topology-aware)
    elif command_lower.startswith("ping"):
        target = command.split()[1] if len(command.split()) > 1 else "127.0.0.1"
        import collections
        import ipaddress
        import json
        import re

        def _extract_ips(dev):
            ips = set()
            try:
                if dev.interfaces:
                    j = json.loads(dev.interfaces)
                    # if interfaces stored as list of objects with 'ip' or 'address', extract directly
                    if isinstance(j, list):
                        for item in j:
                            if isinstance(item, dict):
                                if item.get("address"):
                                    ips.add(item.get("address"))
                                elif item.get("ip"):
                                    # ip might be '1.2.3.4/32'
                                    parts = str(item.get("ip")).split("/")[0]
                                    ips.add(parts)
                                else:
                                    # fallback: scan strings inside dict
                                    for v in item.values():
                                        if isinstance(v, str):
                                            for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", v):
                                                ips.add(m)
                            elif isinstance(item, str):
                                for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", item):
                                    ips.add(m)
                    else:

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

        try:
            ipaddress.ip_address(target)
        except Exception:
            return f"% Unknown host {target}\n"

        # Build adjacency from lab_config.links if present, else auto-generate same as lab_topology
        lab = device.lab
        devices = {d.device_name: d for d in LabDevice.query.filter_by(lab_id=lab.id).all()}
        adj = collections.defaultdict(list)
        links = []
        try:
            cfg = json.loads(lab.lab_config or "{}")
            links = cfg.get("links", []) or []
        except Exception:
            links = []

        if links:
            for link in links:
                if isinstance(link, dict):
                    a = link.get("from")
                    b = link.get("to")
                    if a in devices and b in devices:
                        adj[a].append(b)
                        adj[b].append(a)
                elif isinstance(link, (list, tuple)) and len(link) >= 2 and link[0] in devices and link[1] in devices:
                    adj[link[0]].append(link[1])
                    adj[link[1]].append(link[0])
        else:
            # Auto-generate connections (same rules as lab_topology)
            routers = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "router"]
            switches = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "switch"]
            pcs = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "pc"]
            for i in range(len(routers) - 1):
                a, b = routers[i], routers[i + 1]
                adj[a].append(b)
                adj[b].append(a)
            if routers:
                main_router = routers[0]
                for sw in switches:
                    adj[sw].append(main_router)
                    adj[main_router].append(sw)
            else:
                for i in range(len(switches) - 1):
                    a, b = switches[i], switches[i + 1]
                    adj[a].append(b)
                    adj[b].append(a)
            if switches:
                main_switch = switches[0]
                for pc in pcs:
                    adj[pc].append(main_switch)
                    adj[main_switch].append(pc)
            elif routers:
                main_router = routers[0]
                for pc in pcs:
                    adj[pc].append(main_router)
                    adj[main_router].append(pc)

        # Find devices that own the target IP
        targets = [name for name, d in devices.items() if target in _extract_ips(d)]

        # BFS from source device
        src = device.device_name
        visited = set([src])
        q = collections.deque([[src]])
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

        if path:
            # reachable
            return f"""Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
!!!!!
Success rate is 100 percent (5/5), round-trip min/avg/max = 1/2/4 ms"""
        else:
            return f"""Sending 5, 100-byte ICMP Echos to {target}, timeout is 2 seconds:
.....
Success rate is 0 percent (0/5), round-trip min/avg/max = 0/0/0 ms
Destination host unreachable"""
    # Traceroute command (topology-aware)
    elif command_lower.startswith("traceroute") or command_lower.startswith("tracert"):
        target = command.split()[1] if len(command.split()) > 1 else "8.8.8.8"
        import collections
        import ipaddress
        import json
        import re

        # validate target
        try:
            ipaddress.ip_address(target)
        except Exception:
            return f"% Unknown host {target}\n"

        lab = device.lab
        devices = {d.device_name: d for d in LabDevice.query.filter_by(lab_id=lab.id).all()}
        adj = collections.defaultdict(list)
        links = []
        try:
            cfg = json.loads(lab.lab_config or "{}")
            links = cfg.get("links", []) or []
        except Exception:
            links = []
        if links:
            for link in links:
                if isinstance(link, dict):
                    a = link.get("from")
                    b = link.get("to")
                    if a in devices and b in devices:
                        adj[a].append(b)
                        adj[b].append(a)
                elif isinstance(link, (list, tuple)) and len(link) >= 2 and link[0] in devices and link[1] in devices:
                    adj[link[0]].append(link[1])
                    adj[link[1]].append(link[0])
        else:
            # simple fallback
            routers = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "router"]
            switches = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "switch"]
            pcs = [d.device_name for d in devices.values() if d.device_type and d.device_type.lower() == "pc"]
            for i in range(len(routers) - 1):
                a, b = routers[i], routers[i + 1]
                adj[a].append(b)
                adj[b].append(a)
            if routers:
                main_router = routers[0]
                for sw in switches:
                    adj[sw].append(main_router)
                    adj[main_router].append(sw)
            else:
                for i in range(len(switches) - 1):
                    a, b = switches[i], switches[i + 1]
                    adj[a].append(b)
                    adj[b].append(a)
            if switches:
                main_switch = switches[0]
                for pc in pcs:
                    adj[pc].append(main_switch)
                    adj[main_switch].append(pc)
            elif routers:
                main_router = routers[0]
                for pc in pcs:
                    adj[pc].append(main_router)
                    adj[main_router].append(pc)

        # extract IPs helper
        def _extract_ips(dev):
            import re

            ips = set()
            if dev.interfaces:
                try:
                    j = json.loads(dev.interfaces)
                    if isinstance(j, list):
                        for item in j:
                            if isinstance(item, dict):
                                if item.get("address"):
                                    ips.add(item.get("address"))
                                elif item.get("ip"):
                                    parts = str(item.get("ip")).split("/")[0]
                                    ips.add(parts)
                                else:
                                    for v in item.values():
                                        if isinstance(v, str):
                                            for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", v):
                                                ips.add(m)
                            elif isinstance(item, str):
                                for m in re.findall(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", item):
                                    ips.add(m)
                    else:

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

        targets = [name for name, d in devices.items() if target in _extract_ips(d)]

        # BFS for path
        src = device.device_name
        visited = set([src])
        import collections

        q = collections.deque([[src]])
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

        if path:
            # format hop output using link cost as latency if present
            lines = [f"Tracing the route to {target}"]
            hop = 1

            # helper to find link metadata between two nodes
            def _find_link(a, b, links_list):
                for link in links_list:
                    if isinstance(link, dict):
                        if (link.get("from") == a and link.get("to") == b) or (
                            link.get("from") == b and link.get("to") == a
                        ):
                            return link
                    elif isinstance(link, (list, tuple)) and len(link) >= 2:
                        if (link[0] == a and link[1] == b) or (link[0] == b and link[1] == a):
                            return None
                return None

            for i, n in enumerate(path):
                latency = 1
                iface_info = ""
                if i > 0:
                    prev = path[i - 1]
                    link_meta = _find_link(prev, n, links)
                    if isinstance(link_meta, dict) and "cost" in link_meta:
                        try:
                            base_cost = int(link_meta.get("cost", 1))
                        except Exception:
                            base_cost = 1
                        try:
                            jitter = int(link_meta.get("jitter", 0))
                        except Exception:
                            jitter = 0
                        # determine jitter sampling
                        jval = 0
                        try:
                            import random

                            cfg_all = json.loads(lab.lab_config or "{}")
                            seed = cfg_all.get("jitter_seed")
                            # use per-link deterministic sampling with seed + index
                            if seed is not None:
                                rnd = random.Random(int(seed) + i)
                            else:
                                rnd = random.Random()
                            if jitter > 0:
                                jval = rnd.randint(0, jitter)
                        except Exception:
                            jval = 0
                        latency = max(1, base_cost + jval)
                    # interface labels
                    if isinstance(link_meta, dict) and link_meta.get("src_if") and link_meta.get("dst_if"):
                        iface_info = f" ({link_meta.get('src_if')}↔{link_meta.get('dst_if')})"
                a = max(1, latency - 1)
                b = latency
                c = latency + 1
                lines.append(f"  {hop} {n}{iface_info} [simulated] {a} msec {b} msec {c} msec")
                hop += 1
            return "\n".join(lines)
        else:
            return f"Tracing the route to {target}\n  * * *"
    # Copy command
    elif (
        command_lower.startswith("copy running-config startup-config")
        or command_lower.startswith("copy run start")
        or command_lower == "wr"
    ):
        return """Destination filename [startup-config]?
Building configuration...
[OK]"""

    # Reload command
    elif command_lower == "reload":
        return "System configuration has been modified. Save? [yes/no]:"

    # Write command
    elif command_lower == "write" or command_lower.startswith("write memory"):
        return "Building configuration...\n[OK]"

    # Default: unknown command
    else:
        return (
            f"% Invalid input detected at '^' marker.\n\nUnknown command: {command}\nType '?' for available commands."
        )


def handle_show_command(device, command_lower):
    """Handle various show commands"""

    # Show version
    if "version" in command_lower:
        return (
            f"Cisco IOS Software, {device.model} Software "
            f"({device.model.replace(' ', '_')}-ADVENTERPRISEK9-M), Version 15.4(3)S2\n"
            "Copyright (c) 1986-2015 by Cisco Systems, Inc.\n"
            "Compiled Thu 26-Mar-15 14:31 by prod_rel_team\n\n"
            "ROM: System Bootstrap, Version 15.0(1r)SG16, RELEASE SOFTWARE (fc1)\n\n"
            f"{device.device_name} uptime is 2 weeks, 3 days, 1 hour, 25 minutes\n"
            "System returned to ROM by power-on\n"
            "System image file is \"bootflash:/isr4300-universalk9.154-3.S2.bin\"\n"
            "Last reload type: Normal Reload\n"
        )

    # Show IP interface brief
    elif "ip interface brief" in command_lower or "ip int brief" in command_lower:
        return """Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0/0        192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/0/1        unassigned      YES NVRAM  administratively down down
GigabitEthernet0/0/2        unassigned      YES NVRAM  administratively down down
Loopback0                    10.0.0.1        YES NVRAM  up                    up
"""

    # Show running-config
    elif "running-config" in command_lower or (
        "run" in command_lower and "config" not in command_lower.replace("running-config", "")
    ):
        return device.initial_config or "No configuration available"

    # Show startup-config
    elif "startup-config" in command_lower or "start" in command_lower:
        return device.initial_config or "No configuration available"

    # Show interfaces
    elif "interface" in command_lower or "interfaces" in command_lower:
        if "brief" in command_lower:
            return """Interface                  IP-Address      OK? Method Status                Protocol
GigabitEthernet0/0/0        192.168.1.1     YES NVRAM  up                    up
GigabitEthernet0/0/1        unassigned      YES NVRAM  administratively down down
Loopback0                    10.0.0.1        YES NVRAM  up                    up
"""
        else:
            return """GigabitEthernet0/0/0 is up, line protocol is up
  Hardware is Gigabit Ethernet, address is 0000.0000.0001 (bia 0000.0000.0001)
  Internet address is 192.168.1.1/24
  MTU 1500 bytes, BW 1000000 Kbit/sec, DLY 10 usec,
     reliability 255/255, txload 1/255, rxload 1/255
"""

    # Show IP route
    elif "ip route" in command_lower or "ip-route" in command_lower:
        return """Codes: L - local, C - connected, S - static, R - RIP, M - mobile, B - BGP
       D - EIGRP, EX - EIGRP external, O - OSPF, IA - OSPF inter area
       N1 - OSPF NSSA external type 1, N2 - OSPF NSSA external type 2
       E1 - OSPF external type 1, E2 - OSPF external type 2
       i - IS-IS, su - IS-IS summary, L1 - IS-IS level-1, L2 - IS-IS level-2
       ia - IS-IS inter area, * - candidate default, U - per-user static route
       o - ODR, P - periodic downloaded static route, H - NHRP, l - LISP
       a - application route
       + - replicated route, % - next hop override

Gateway of last resort is not set

      10.0.0.0/8 is variably subnetted, 2 subnets, 2 masks
C        10.0.0.0/24 is directly connected, Loopback0
L        10.0.0.1/32 is directly connected, Loopback0
      192.168.1.0/24 is variably subnetted, 2 subnets, 2 masks
C        192.168.1.0/24 is directly connected, GigabitEthernet0/0/0
L        192.168.1.1/32 is directly connected, GigabitEthernet0/0/0
"""

    # Show VLAN
    elif "vlan" in command_lower:
        if device.device_type.lower() == "switch":
            return """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3, Fa0/4
10   Sales                            active    Fa0/11, Fa0/12
20   Engineering                      active    Fa0/21, Fa0/22
100  Management                       active
1002 fddi-default                     act/unsup
1003 token-ring-default               act/unsup
"""
        else:
            return "VLANs are not supported on router interfaces"

    # Show VLAN brief
    elif "vlan brief" in command_lower:
        return """VLAN Name                             Status    Ports
---- -------------------------------- --------- -------------------------------
1    default                          active    Fa0/1, Fa0/2, Fa0/3
10   Sales                            active    Fa0/11, Fa0/12
20   Engineering                      active    Fa0/21, Fa0/22
"""

    # Show IP OSPF
    elif "ospf" in command_lower:
        return """Routing Process "ospf 1" with ID 1.1.1.1
Start time: 00:00:00.000, Time elapsed: 2w3d
Supports only single TOS(TOS0) routes
Supports opaque LSA
Supports Link-local Signaling (LLS)
Supports area transit capability
Router is not originating router-LSAs with maximum metric
Initial SPF schedule delay 5000 msec
Minimum hold time between two consecutive SPFs 10000 msec
Maximum wait time between two consecutive SPFs 10000 msec
"""

    # Show IP EIGRP
    elif "eigrp" in command_lower:
        return """IP-EIGRP AS 100 ID 1.1.1.1
  EIGRP-IPv4 Protocol for AS(100)
    Metric weight K1=1, K2=0, K3=1, K4=0, K5=0
    NSF-aware route hold timer is 240
    Router-ID: 1.1.1.1
    Topology : 0 (base)
      Active Timer: 3 min
      Distance: internal 90 external 170
      Maximum path: 4
"""

    # Show IP access-list
    elif "access-list" in command_lower or "acl" in command_lower:
        return """Standard IP access list 10
    10 permit 192.168.1.0, wildcard bits 0.0.0.255
    20 permit 10.0.0.0, wildcard bits 0.0.0.255
Extended IP access list 100
    10 permit tcp any any eq www
    20 permit tcp any any eq 443
    30 deny   ip any any
"""

    # Show IP arp
    elif "arp" in command_lower:
        return """Protocol  Address          Age (min)  Hardware Addr   Type   Interface
Internet  192.168.1.1             -   0000.0000.0001  ARPA   GigabitEthernet0/0/0
Internet  192.168.1.2             5   0000.0000.0002  ARPA   GigabitEthernet0/0/0
"""

    # Show CDP neighbors
    elif "cdp" in command_lower:
        return """Capability Codes: R - Router, T - Trans Bridge, B - Source Route Bridge
                  S - Switch, H - Host, I - IGMP, r - Repeater, P - Phone,
                  D - Remote, C - CVTA, M - Two-port Mac Relay

Device ID        Local Intrfce     Holdtme    Capability  Platform  Port ID
R2               Gig 0/0/0         157              R     ISR4331   Gig 0/0/0
SW1              Gig 0/0/1         145              S     C2960     Gig 0/1

Total cdp entries displayed : 2
"""

    # Show spanning-tree
    elif "spanning-tree" in command_lower or "stp" in command_lower:
        return """VLAN0001
  Spanning tree enabled protocol ieee
  Root ID    Priority    32769
             Address     0000.0000.0001
             This bridge is the root
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec

  Bridge ID  Priority    32769  (priority 32768 sys-id-ext 1)
             Address     0000.0000.0001
             Hello Time   2 sec  Max Age 20 sec  Forward Delay 15 sec
             Aging Time  300 sec

Interface           Role Sts Cost      Prio.Nbr Type
------------------- ---- --- --------- -------- --------------------------------
Fa0/1               Desg FWD 19        128.1    P2p
"""

    # Show MAC address-table (switch)
    elif "mac" in command_lower or "mac-address" in command_lower:
        if device.device_type.lower() == "switch":
            return """          Mac Address Table
-------------------------------------------

Vlan    Mac Address       Type        Ports
----    -----------       --------    -----
   1    0000.0000.0001    DYNAMIC     Fa0/1
   1    0000.0000.0002    DYNAMIC     Fa0/2
  10    0000.0000.0010    DYNAMIC     Fa0/11
  20    0000.0000.0020    DYNAMIC     Fa0/21
Total Mac Addresses for this criterion: 4
"""
        else:
            return "MAC address table is not available on routers"

    # Show clock
    elif "clock" in command_lower:
        return "*00:00:00.000 UTC Mon Jan 1 2025"

    # Show users
    elif "users" in command_lower:
        return """    Line       User       Host(s)              Idle       Location
*  0 con 0    admin      idle                 00:00:00
   1 vty 0    user1      idle                 00:05:00 192.168.1.100
"""

    # Show protocols
    elif "protocols" in command_lower or "protocol" in command_lower:
        return """Global values:
  Internet Protocol routing is enabled
"""

    # Show flash
    elif "flash" in command_lower:
        return """-#- --length-- -----date/time------ path
1    84510720   Jan 1 2025 00:00:00 +00:00 isr4300-universalk9.154-3.S2.bin
2    1024       Jan 1 2025 00:00:00 +00:00 startup-config

84511744 bytes available (84510720 bytes used)
"""

    # Default show command
    else:
        return (
            "Command not fully simulated. Available show commands:\n"
            "  version, ip interface brief, running-config, ip route, vlan, ospf, eigrp, "
            "access-list, arp, cdp, spanning-tree, mac address-table"
        )


def simulate_arista_command(device, command):
    """Simulate Arista EOS command execution"""
    command_lower = command.strip().lower()

    if command_lower == "enable" or command_lower == "en":
        return "Password: \n"

    elif command_lower.startswith("show") or command_lower.startswith("sh"):
        if "version" in command_lower:
            return """Arista DCS-7050SX
Hardware version:    01.01
Serial number:       JPE12345678
System MAC address:  0000.0000.0001

Software image version: 4.27.0F
Architecture:           i386
Internal build version: 4.27.0F-12345678.4270F
Internal build ID:      abc12345
Uptime:                 2 weeks, 3 days, 1 hour, 25 minutes
Total memory:           4094976 kB
Free memory:            2047488 kB
"""
        elif "ip interface brief" in command_lower or "ip int brief" in command_lower:
            return """Interface         IP Address         Status         Protocol         MTU
Ethernet1        unassigned         up             up              1500
Ethernet2        unassigned         up             up              1500
Management1      192.168.1.1/24     up             up              1500
"""
        elif "running-config" in command_lower:
            return device.initial_config or "No configuration available"
        elif "vlan" in command_lower:
            return """VLAN  Name                             Status    Ports
----- -------------------------------- --------- -------------------------------
1     default                          active    Et1, Et2
100   Management                       active    Et10
200   VLAN200                          active
"""
        else:
            return "Available show commands: version, ip interface brief, running-config, vlan"

    elif command_lower.startswith("configure") or command_lower.startswith("conf"):
        return "Entering configuration mode terminal"

    elif command_lower.startswith("interface") or command_lower.startswith("int "):
        name = command.split()[-1] if len(command.split()) > 1 else "interface"
        return f"Entering interface configuration mode for {name}"

    elif command_lower == "exit" or command_lower == "end":
        return ""

    elif command_lower == "?":
        return """Available commands:
  configure     Enter configuration mode
  show          Show running system information
  enable        Enter privileged mode
  exit          Exit current mode
  ping          Send ICMP echo messages
  traceroute    Trace route to destination
"""
    else:
        return f"Unknown command: {command}\nType '?' for available commands."


@app.route("/api/cleanup/isolated-devices", methods=["POST"])
@login_required
def cleanup_isolated_devices():
    """Remove all ISOLATED devices from all labs"""
    if not current_user.is_admin:
        return jsonify({"success": False, "error": "Admin access required"}), 403

    isolated_devices = db.session.scalars(
        select(LabDevice).filter(or_(LabDevice.device_type == "Isolated", LabDevice.device_name.like("ISOLATED%")))
    ).all()

    count = len(isolated_devices)
    for device in isolated_devices:
        db.session.delete(device)
    db.session.commit()

    return jsonify({"success": True, "removed": count})


@app.route("/api/lab/<int:lab_id>/save", methods=["POST"])
@login_required
def save_lab_progress(lab_id):
    """Save user's lab progress"""
    user_lab = db.session.query(UserLab).filter_by(user_id=current_user.id, lab_id=lab_id).first()
    if user_lab is None:
        abort(404)
    data = request.get_json()

    if "config" in data:
        user_lab.current_config = data["config"]
    if "status" in data:
        user_lab.status = data["status"]
        if data["status"] == "Completed":
            user_lab.completed_at = datetime.utcnow()
            current_user.labs_completed += 1

    db.session.commit()
    return jsonify({"success": True})


# Initialize database
def init_db():
    """Create database tables and sample data"""
    db.create_all()

    # Remove all ISOLATED devices from all labs
    isolated_devices = db.session.scalars(
        select(LabDevice).filter(or_(LabDevice.device_type == "Isolated", LabDevice.device_name.like("ISOLATED%")))
    ).all()
    for device in isolated_devices:
        db.session.delete(device)

    # Remove R3 devices with Generic vendor and v1 model from Basic Router Configuration lab
    basic_lab = db.session.scalars(select(Lab).filter_by(title="Basic Router Configuration")).first()
    if basic_lab:
        r3_devices = db.session.scalars(
            select(LabDevice).filter_by(lab_id=basic_lab.id, device_name="R3", vendor="Generic", model="v1")
        ).all()
        for device in r3_devices:
            db.session.delete(device)

    db.session.commit()

    # Create sample labs if none exist
    if db.session.scalar(select(func.count()).select_from(Lab)) == 0:
        # Sample Lab 1: Basic Router Configuration
        lab1 = Lab(
            title="Basic Router Configuration",
            description="Learn to configure a Cisco router with IP addresses, static routes, and basic connectivity.",
            difficulty="Beginner",
            category="Routing",
            lab_config='{"devices": ["R1", "R2", "SW1"], "topology": "point-to-point"}',
        )
        db.session.add(lab1)

        device1 = LabDevice(
            lab=lab1,
            device_name="R1",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface Loopback0
 ip address 10.0.0.1 255.255.255.255
end""",
        )
        db.session.add(device1)

        # Add second router to the basic lab so students can practice point-to-point links
        device1b = LabDevice(
            lab=lab1,
            device_name="R2",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R2
interface GigabitEthernet0/0/0
 ip address 192.168.1.2 255.255.255.0
 no shutdown
interface Loopback0
 ip address 10.0.0.2 255.255.255.255
end""",
        )
        db.session.add(device1b)

        # Add a simple access switch to the basic lab
        device1_switch = LabDevice(
            lab=lab1,
            device_name="SW1",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW1
vlan 10
 name Users
interface range FastEthernet0/1-2
 switchport mode access
 switchport access vlan 10
interface GigabitEthernet1/0/48
 switchport mode trunk
 switchport trunk allowed vlan 10
end""",
        )
        db.session.add(device1_switch)

        # Sample Lab 2: VLAN Configuration
        lab2 = Lab(
            title="VLAN Configuration on Switch",
            description="Configure VLANs on a Cisco switch and assign ports to VLANs.",
            difficulty="Beginner",
            category="Switching",
            lab_config='{"devices": ["SW1"], "topology": "single-switch"}',
        )
        db.session.add(lab2)

        device2 = LabDevice(
            lab=lab2,
            device_name="SW1",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW1
vlan 10
 name Sales
vlan 20
 name Engineering
interface range FastEthernet0/1-10
 switchport mode access
 switchport access vlan 10
end""",
        )
        db.session.add(device2)

        # Sample Lab 3: Arista Switch Configuration
        lab3 = Lab(
            title="Arista Switch Configuration",
            description="Configure an Arista switch with VLANs and trunk ports.",
            difficulty="Intermediate",
            category="Switching",
            lab_config='{"devices": ["AR1"], "topology": "single-switch"}',
        )
        db.session.add(lab3)

        device3 = LabDevice(
            lab=lab3,
            device_name="AR1",
            device_type="Switch",
            vendor="Arista",
            model="DCS-7050SX",
            initial_config="""hostname AR1
vlan 100
   name Management
interface Ethernet1
   switchport mode trunk
   switchport trunk allowed vlan 100,200
end""",
        )
        db.session.add(device3)

        # Sample Lab 4: OSPF Routing Configuration
        lab4 = Lab(
            title="OSPF Routing Configuration",
            description="Configure OSPF routing protocol on multiple routers to establish dynamic routing.",
            difficulty="Intermediate",
            category="Routing",
            lab_config='{"devices": ["R1", "R2", "R3"], "topology": "multi-router"}',
        )
        db.session.add(lab4)

        device4 = LabDevice(
            lab=lab4,
            device_name="R1",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface Loopback0
 ip address 1.1.1.1 255.255.255.255
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 1.1.1.1 0.0.0.0 area 0
end""",
        )
        db.session.add(device4)

        device4b = LabDevice(
            lab=lab4,
            device_name="R2",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R2
interface GigabitEthernet0/0/0
 ip address 192.168.1.2 255.255.255.0
 no shutdown
interface GigabitEthernet0/0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
interface Loopback0
 ip address 2.2.2.2 255.255.255.255
router ospf 1
 network 192.168.1.0 0.0.0.255 area 0
 network 192.168.2.0 0.0.0.255 area 0
 network 2.2.2.2 0.0.0.0 area 0
end""",
        )
        db.session.add(device4b)

        # Sample Lab 5: EIGRP Configuration
        lab5 = Lab(
            title="EIGRP Routing Configuration",
            description="Configure EIGRP routing protocol for dynamic routing in a small network.",
            difficulty="Intermediate",
            category="Routing",
            lab_config='{"devices": ["R1", "R2"], "topology": "point-to-point"}',
        )
        db.session.add(lab5)

        device5 = LabDevice(
            lab=lab5,
            device_name="R1",
            device_type="Router",
            vendor="Cisco",
            model="ISR4321",
            initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 10.1.1.1 255.255.255.252
 no shutdown
router eigrp 100
 network 10.1.1.0 0.0.0.3
 no auto-summary
end""",
        )
        db.session.add(device5)

        # Sample Lab 6: Access Control Lists (ACLs)
        lab6 = Lab(
            title="Access Control Lists (ACLs)",
            description="Configure standard and extended ACLs to control network traffic and secure your network.",
            difficulty="Intermediate",
            category="Security",
            lab_config='{"devices": ["R1"], "topology": "single-router"}',
        )
        db.session.add(lab6)

        device6 = LabDevice(
            lab=lab6,
            device_name="R1",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 192.168.1.1 255.255.255.0
 no shutdown
interface GigabitEthernet0/0/1
 ip address 10.0.0.1 255.255.255.0
 no shutdown
access-list 10 permit 192.168.1.0 0.0.0.255
access-list 10 deny any
ip access-group 10 out
end""",
        )
        db.session.add(device6)

        # Sample Lab 7: Spanning Tree Protocol (STP)
        lab7 = Lab(
            title="Spanning Tree Protocol (STP)",
            description="Configure and troubleshoot STP on switches to prevent loops in a switched network.",
            difficulty="Intermediate",
            category="Switching",
            lab_config='{"devices": ["SW1", "SW2"], "topology": "multi-switch"}',
        )
        db.session.add(lab7)

        device7 = LabDevice(
            lab=lab7,
            device_name="SW1",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW1
spanning-tree mode rapid-pvst
spanning-tree vlan 1 priority 4096
interface FastEthernet0/1
 switchport mode trunk
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 10
end""",
        )
        db.session.add(device7)

        device7b = LabDevice(
            lab=lab7,
            device_name="SW2",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW2
spanning-tree mode rapid-pvst
spanning-tree vlan 1 priority 8192
interface FastEthernet0/1
 switchport mode trunk
interface FastEthernet0/2
 switchport mode access
 switchport access vlan 20
end""",
        )
        db.session.add(device7b)

        # Sample Lab 8: Static Routing
        lab8 = Lab(
            title="Static Routing Configuration",
            description="Configure static routes on routers to enable connectivity between different networks.",
            difficulty="Beginner",
            category="Routing",
            lab_config='{"devices": ["R1", "R2"], "topology": "point-to-point"}',
        )
        db.session.add(lab8)

        device8 = LabDevice(
            lab=lab8,
            device_name="R1",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 192.168.1.1 255.255.255.252
 no shutdown
interface GigabitEthernet0/0/1
 ip address 10.1.1.1 255.255.255.0
 no shutdown
ip route 192.168.2.0 255.255.255.0 192.168.1.2
end""",
        )
        db.session.add(device8)

        device8b = LabDevice(
            lab=lab8,
            device_name="R2",
            device_type="Router",
            vendor="Cisco",
            model="ISR4331",
            initial_config="""hostname R2
interface GigabitEthernet0/0/0
 ip address 192.168.1.2 255.255.255.252
 no shutdown
interface GigabitEthernet0/0/1
 ip address 192.168.2.1 255.255.255.0
 no shutdown
ip route 10.1.1.0 255.255.255.0 192.168.1.1
end""",
        )
        db.session.add(device8b)

        # Sample Lab 9: Trunk Configuration
        lab9 = Lab(
            title="Trunk Configuration between Switches",
            description="Configure trunk ports to carry multiple VLANs between switches.",
            difficulty="Intermediate",
            category="Switching",
            lab_config='{"devices": ["SW1", "SW2"], "topology": "multi-switch"}',
        )
        db.session.add(lab9)

        device9 = LabDevice(
            lab=lab9,
            device_name="SW1",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW1
vlan 10
 name Sales
vlan 20
 name Engineering
interface FastEthernet0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end""",
        )
        db.session.add(device9)

        device9b = LabDevice(
            lab=lab9,
            device_name="SW2",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW2
vlan 10
 name Sales
vlan 20
 name Engineering
interface FastEthernet0/24
 switchport mode trunk
 switchport trunk allowed vlan 10,20
end""",
        )
        db.session.add(device9b)

        # Sample Lab 10: Port Security
        lab10 = Lab(
            title="Port Security Configuration",
            description="Configure port security on switch interfaces to limit and control MAC addresses.",
            difficulty="Intermediate",
            category="Security",
            lab_config='{"devices": ["SW1"], "topology": "single-switch"}',
        )
        db.session.add(lab10)

        device10 = LabDevice(
            lab=lab10,
            device_name="SW1",
            device_type="Switch",
            vendor="Cisco",
            model="Catalyst 2960",
            initial_config="""hostname SW1
interface FastEthernet0/1
 switchport mode access
 switchport port-security
 switchport port-security maximum 2
 switchport port-security violation restrict
 switchport port-security mac-address sticky
end""",
        )
        db.session.add(device10)

        # Sample Lab 11: Arista Multi-VLAN Configuration
        lab11 = Lab(
            title="Arista Multi-VLAN and Trunking",
            description="Configure multiple VLANs and trunk ports on Arista switches using EOS commands.",
            difficulty="Advanced",
            category="Switching",
            lab_config='{"devices": ["AR1", "AR2"], "topology": "multi-switch"}',
        )
        db.session.add(lab11)

        device11 = LabDevice(
            lab=lab11,
            device_name="AR1",
            device_type="Switch",
            vendor="Arista",
            model="DCS-7050TX",
            initial_config="""hostname AR1
vlan 100
   name Management
vlan 200
   name Servers
vlan 300
   name Users
interface Ethernet1
   switchport mode trunk
   switchport trunk allowed vlan 100,200,300
interface Ethernet2
   switchport mode access
   switchport access vlan 200
end""",
        )
        db.session.add(device11)

        device11b = LabDevice(
            lab=lab11,
            device_name="AR2",
            device_type="Switch",
            vendor="Arista",
            model="DCS-7050TX",
            initial_config="""hostname AR2
vlan 100
   name Management
vlan 200
   name Servers
vlan 300
   name Users
interface Ethernet1
   switchport mode trunk
   switchport trunk allowed vlan 100,200,300
interface Ethernet2
   switchport mode access
   switchport access vlan 300
end""",
        )
        db.session.add(device11b)

        # Sample Lab 12: Cisco Nexus Switch (NX-OS)
        lab12 = Lab(
            title="Cisco Nexus Switch Configuration",
            description="Configure a Cisco Nexus switch with VLANs and basic switching features using NX-OS.",
            difficulty="Advanced",
            category="Switching",
            lab_config='{"devices": ["NX1"], "topology": "single-switch"}',
        )
        db.session.add(lab12)

        device12 = LabDevice(
            lab=lab12,
            device_name="NX1",
            device_type="Switch",
            vendor="Cisco",
            model="Nexus 9000",
            initial_config="""hostname NX1
vlan 10
  name Production
vlan 20
  name Development
interface Ethernet1/1
  switchport mode trunk
  switchport trunk allowed vlan 10,20
interface Ethernet1/2
  switchport mode access
  switchport access vlan 10
end""",
        )
        db.session.add(device12)

        db.session.commit()

    # Ensure key devices exist (idempotent) for Basic Router Configuration lab
    basic_lab = db.session.scalars(select(Lab).filter_by(title="Basic Router Configuration")).first()
    if basic_lab:
        # Add R2 if missing
        if not db.session.scalars(select(LabDevice).filter_by(lab_id=basic_lab.id, device_name="R2")).first():
            r2 = LabDevice(
                lab=basic_lab,
                device_name="R2",
                device_type="Router",
                vendor="Cisco",
                model="ISR4331",
                initial_config="""hostname R2
interface GigabitEthernet0/0/0
 ip address 192.168.1.2 255.255.255.0
 no shutdown
interface Loopback0
 ip address 10.0.0.2 255.255.255.255
end""",
            )
            db.session.add(r2)
        # Add SW1 if missing
        if not db.session.scalars(select(LabDevice).filter_by(lab_id=basic_lab.id, device_name="SW1")).first():
            sw1 = LabDevice(
                lab=basic_lab,
                device_name="SW1",
                device_type="Switch",
                vendor="Cisco",
                model="Catalyst 2960",
                initial_config="""hostname SW1
vlan 10
 name Users
interface range FastEthernet0/1-2
 switchport mode access
 switchport access vlan 10
interface GigabitEthernet1/0/48
 switchport mode trunk
 switchport trunk allowed vlan 10
end""",
            )
            db.session.add(sw1)
        # Add PC1 if missing
        if not db.session.scalars(select(LabDevice).filter_by(lab_id=basic_lab.id, device_name="PC1")).first():
            pc1 = LabDevice(
                lab=basic_lab,
                device_name="PC1",
                device_type="PC",
                vendor="Generic",
                model="Virtual PC",
                initial_config="""hostname PC1
# This PC is simulated. Use the Browser action to simulate HTTP/DNS requests.
""",
            )
            db.session.add(pc1)
        db.session.commit()

    # Ensure devices referenced in lab.lab_config exist (add with simple heuristics if missing)
    import json

    for lab in db.session.scalars(select(Lab)).all():
        try:
            cfg = json.loads(lab.lab_config or "{}")
        except Exception:
            cfg = {}
        names = cfg.get("devices") or []
        for name in names:
            # Skip R3 for Basic Router Configuration lab
            if lab.title == "Basic Router Configuration" and name == "R3":
                continue

            if not db.session.scalars(select(LabDevice).filter_by(lab_id=lab.id, device_name=name)).first():
                # heuristics for device type/vendor
                if name.upper().startswith("R"):
                    dtype = "Router"
                    vendor = "Cisco"
                    model = "ISR4331"
                elif name.upper().startswith("SW"):
                    dtype = "Switch"
                    vendor = "Cisco"
                    model = "Catalyst 2960"
                elif name.upper().startswith("AR"):
                    dtype = "Switch"
                    vendor = "Arista"
                    model = "DCS-7050SX"
                elif name.upper().startswith("PC"):
                    dtype = "PC"
                    vendor = "Generic"
                    model = "Virtual PC"
                else:
                    dtype = "Switch"
                    vendor = "Generic"
                    model = "Virtual"
                default_cfg = f"hostname {name}\n"
                db.session.add(
                    LabDevice(
                        lab=lab,
                        device_name=name,
                        device_type=dtype,
                        vendor=vendor,
                        model=model,
                        initial_config=default_cfg,
                    )
                )
        db.session.commit()

    # Add router R1 to Arista lab (and link it to AR1) if missing
    arista_lab = db.session.scalars(select(Lab).filter_by(title="Arista Switch Configuration")).first()
    if arista_lab:
        if not db.session.scalars(select(LabDevice).filter_by(lab_id=arista_lab.id, device_name="R1")).first():
            r1 = LabDevice(
                lab=arista_lab,
                device_name="R1",
                device_type="Router",
                vendor="Cisco",
                model="ISR4331",
                initial_config="""hostname R1
interface GigabitEthernet0/0/0
 ip address 192.168.10.1 255.255.255.0
 no shutdown
end""",
            )
            db.session.add(r1)
            db.session.commit()
        # ensure a link exists between AR1 and R1
        try:
            cfg = json.loads(arista_lab.lab_config or "{}")
        except Exception:
            cfg = {}
        links = cfg.get("links") or []
        if ["AR1", "R1"] not in links and ["R1", "AR1"] not in links:
            links.append(["AR1", "R1"])
            cfg["links"] = links
            arista_lab.lab_config = json.dumps(cfg)
            db.session.commit()


# Ensure database is initialized on import (helps tests and CI)
with app.app_context():
    init_db()

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
