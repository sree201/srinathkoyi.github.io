# CCNA Practice Platform

A comprehensive Python-based platform for CCNA networking practice, similar to DevOps-Xlabs. Practice on Cisco routers, switches, and Arista devices with hands-on lab environments.

## Features

- **User Authentication**: Register and login system for user management
- **Lab Management**: Create and manage CCNA practice labs
- **Device Support**: 
  - Cisco Routers (ISR series)
  - Cisco Switches (Catalyst series)
  - Arista Switches (DCS series)

### ✅ Supported Device Models (by role & lab level)

**Routers**

- **Beginner Lab Setup**
  - Cisco ISR 1100 series (recommended for small labs)
- **Advanced / Enterprise Setup**
  - Cisco Catalyst 8300 series
  - Cisco ISR 4331

**Switches**

- **Beginner Lab Setup**
  - Cisco Catalyst 2960 / 2960‑X (great for simple VLAN and port-security labs)
- **Advanced / Enterprise Setup**
  - Cisco Catalyst 9300 series
  - Cisco Nexus 3000 series
  - Cisco Catalyst 9400 / 9500 series

> Additional models included: **Cisco Catalyst 9300 / 9400 / 9500 Series** and **Cisco Catalyst 2960 / 2960‑X** (added for completeness).

---

### 🔧 Topology Examples & Suggestions

**3-node topology (simple learning topology)**
- Typical setup: 2 Routers + 1 Switch (R1 — SW1 — R2) or 3 Routers in a triangle (R1 — R2 — R3).
- Suggested use: practice inter-VLAN routing, static routes, and basic dynamic routing (OSPF/EIGRP).

Example connection suggestion (2 routers + 1 switch):
- R1 Gi0/0/0 <-> SW1 Gi0/1
- R2 Gi0/0/0 <-> SW1 Gi0/2

**7-node topology (enterprise-style)**
- Typical setup: 4 Routers (core/distribution) + 3 Switches (access).
- Example layout: Core: R1, R2, R3 (mesh) ; Dist: R4 ; Access: SW1, SW2, SW3 connected to R4 and interlinked for redundancy.
- Suggested use: multi-area OSPF, VLAN designs with trunking, STP, port-security, and ACL segmentation.

Example connection suggestion (7 nodes):
- R1 <-> R2, R1 <-> R3, R2 <-> R3 (core mesh)
- R4 connects to core (R1/R2/R3) and to access switches SW1, SW2, SW3
- SW1/SW2/SW3 connect to access hosts and to R4 for inter-VLAN routing (or use a router-on-a-stick configuration)

---

### 🛠️ Configuration Examples & Command Quick Reference

> These examples are intentionally concise. Everyone can manually add routers/switches and adjust interfaces/configuration as needed.

#### Basic (Beginner) - common commands

- Enter global config: `configure terminal`
- Interface config example:
  - `interface GigabitEthernet0/0/0`
  - `ip address 192.168.1.1 255.255.255.0`
  - `no shutdown`
- Verify:
  - `show ip interface brief`
  - `show running-config`

#### Switching basics

- Create VLAN: `vlan 10` / `name Users`
- Assign port to VLAN:
  - `interface FastEthernet0/1`
  - `switchport mode access`
  - `switchport access vlan 10`
- Trunking:
  - `interface GigabitEthernet1/0/1`
  - `switchport mode trunk`
  - `switchport trunk allowed vlan 10,20,30`
- Verify:
  - `show vlan brief`
  - `show interfaces trunk`

#### Dynamic routing (examples)

- OSPF (router R1):
  - `router ospf 1`
  - `network 192.168.1.0 0.0.0.255 area 0`
- EIGRP (router R1):
  - `router eigrp 100`
  - `network 10.1.1.0 0.0.0.0`

#### Advanced (Enterprise) - common commands

- Access Control Lists (ACLs):
  - `access-list 101 permit tcp any host 192.168.1.10 eq 80`
  - Apply to interface: `ip access-group 101 in`
- NAT (basic):
  - `ip nat inside source list 1 interface GigabitEthernet0/0/0 overload`
- VLAN & Trunking (VTP optional):
  - `vlan 20`
  - `vlan 30`
  - `switchport trunk encapsulation dot1q`
- Spanning Tree (basic tuning):
  - `spanning-tree mode rapid-pvst`
  - `spanning-tree vlan 1 priority 4096`
- EtherChannel (LACP):
  - `interface Port-channel1`
  - `switchport mode trunk`
  - On member interfaces: `channel-group 1 mode active`

#### Examples for 3-node topology (R1, R2, SW1)

R1 (interface to SW1):
```
interface GigabitEthernet0/0/0
 ip address 10.0.0.1 255.255.255.252
 no shutdown
```

R2 (interface to SW1):
```
interface GigabitEthernet0/0/0
 ip address 10.0.0.2 255.255.255.252
 no shutdown
```

SW1 (access ports and trunk to R1/R2):
```
interface GigabitEthernet1/0/1
 switchport mode access
 switchport access vlan 10
!
interface GigabitEthernet1/0/48
 switchport mode trunk
 switchport trunk allowed vlan 10,20
```

#### Examples for 7-node topology (core/distribution/access)
- Configure core OSPF adjacency across R1/R2/R3, then redistribute to distribution (R4) and access networks via R4.
- Example (R1):
```
interface GigabitEthernet0/0/0
 ip address 172.16.0.1 255.255.255.252
 no shutdown
router ospf 1
 network 172.16.0.0 0.0.0.3 area 0
```

---

If you'd like, I can:
- Add full example configs for each model listed, or
- Provide downloadable sample config files per topology (3-node and 7-node), or
- Add these command cheatsheets as separate markdown files for quick reference.

**Would you like me to add full per-model sample configs or generate sample config files for the lab topologies?**
- **Progress Tracking**: Track your lab completion and progress
- **Modern UI**: Beautiful, responsive design similar to DevOps-Xlabs

## Technology Stack

- **Backend**: Flask (Python)
- **Database**: SQLite (can be upgraded to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: Flask-Login
- **ORM**: SQLAlchemy

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup Instructions

1. **Clone or navigate to the project directory**

```bash
cd CCNA-Website
```

2. **Create a virtual environment (recommended)**

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Initialize the database**

The database will be automatically created when you first run the application.

5. **Run the application**

```bash
python app.py
```

6. **Access the application**

Open your browser and navigate to: `http://localhost:5000`

## Configuration

### Environment Variables (Optional)

Create a `.env` file in the root directory for custom configuration:

```env
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///ccna_labs.db
```

### Database

By default, the application uses SQLite. To use PostgreSQL or MySQL:

1. Install the appropriate database adapter:
   ```bash
   pip install psycopg2-binary  # For PostgreSQL
   # or
   pip install mysqlclient      # For MySQL
   ```

2. Update `DATABASE_URL` in `.env`:
   ```env
   DATABASE_URL=postgresql://user:password@localhost/ccna_labs
   # or
   DATABASE_URL=mysql://user:password@localhost/ccna_labs
   ```

## Usage

### First Time Setup

1. **Register an Account**
   - Click "Register" on the homepage
   - Fill in your username, email, and password
   - Click "Register"

2. **Login**
   - Use your credentials to log in
   - You'll be redirected to your dashboard

3. **Start a Lab**
   - Browse available labs from the "Labs" page
   - Click "Start Lab" on any lab
   - Use the terminal interface to configure devices

### Using the Terminal Interface

The terminal simulates Cisco/Arista device commands:

- **Basic Commands**:
  - `show version` - Display device version
  - `show ip interface brief` - Show interface IPs
  - `show running-config` - Display current configuration
  - `configure terminal` - Enter configuration mode
  - `enable` - Enter privileged EXEC mode
  - `?` - Show available commands

- **Navigation**:
  - Use arrow keys (↑/↓) to navigate command history
  - Tab completion (coming soon)
  - Multiple devices can be accessed via tabs

## Project Structure

```
CCNA-Website/
├── app.py                  # Main Flask application
├── requirements.txt        # Python dependencies
├── .gitignore             # Git ignore file
├── templates/             # HTML templates
│   ├── base.html          # Base template
│   ├── index.html         # Landing page
│   ├── login.html         # Login page
│   ├── register.html      # Registration page
│   ├── dashboard.html     # User dashboard
│   ├── labs.html          # Labs listing
│   └── lab_detail.html    # Lab detail/terminal
├── static/                # Static files
│   ├── css/
│   │   ├── styles.css     # Main stylesheet
│   │   └── terminal.css   # Terminal interface styles
│   └── js/
│       ├── main.js        # Main JavaScript
│       └── terminal.js    # Terminal functionality
└── ccna_labs.db           # SQLite database (created on first run)
```

## Database Models

### User
- User authentication and profile information
- Tracks completed labs

### Lab
- Lab definitions with difficulty, category, and configuration
- Stores lab metadata

### LabDevice
- Network devices (routers/switches) associated with labs
- Stores device configurations and models

### UserLab
- Tracks user progress on each lab
- Stores current configurations and completion status

## Adding New Labs

Labs can be added programmatically through the Flask shell or by extending the `create_tables()` function in `app.py`.

Example:
```python
new_lab = Lab(
    title="OSPF Configuration",
    description="Configure OSPF routing protocol on multiple routers",
    difficulty="Intermediate",
    category="Routing",
    lab_config='{"devices": ["R1", "R2", "R3"]}'
)
db.session.add(new_lab)
db.session.commit()
```

## Future Enhancements

- [ ] Full network emulation integration (GNS3, ContainerLab)
- [ ] Advanced command simulation
- [ ] Lab validation and scoring
- [ ] Video tutorials integration
- [ ] AI-powered lab recommendations
- [ ] Community features (share labs, discussions)
- [ ] More device models and vendors
- [ ] Lab export/import functionality
- [ ] Admin panel for lab management

## Security Notes

- **Production Deployment**: 
  - Change the `SECRET_KEY` in production
  - Use environment variables for sensitive data
  - Enable HTTPS/SSL
  - Use a production-grade database (PostgreSQL recommended)
  - Set up proper session security

## Deployment

### Local Development
```bash
python app.py
```

### Production Deployment

For production, use a WSGI server like Gunicorn:

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

Or use platforms like:
- **Heroku**: Add `Procfile` with `web: gunicorn app:app`
- **AWS**: Deploy on EC2 with Elastic Beanstalk
- **DigitalOcean**: Use App Platform
- **Docker**: Create Dockerfile for containerized deployment

## Contributing

This is a template/platform. Feel free to extend and customize:
- Add more device models
- Implement advanced command parsing
- Integrate with network emulation tools
- Enhance the UI/UX

## License

This project is open source and available for educational purposes.

## Support

For issues or questions, please create an issue in the repository.

---

**Note**: This platform provides simulated network device interaction. For full network emulation, consider integrating with tools like GNS3, ContainerLab, or Cisco Packet Tracer API.
