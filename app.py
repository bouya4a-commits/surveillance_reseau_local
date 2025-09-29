# app.py
import os
import json
import time
import threading
import urllib.request
from datetime import datetime
from collections import defaultdict
from flask import Flask, render_template, jsonify, request
import psutil
import socket

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, 'templates'),
    static_folder=os.path.join(BASE_DIR, 'static')
)

CAPTURES_DIR = "captures"
MALICIOUS_IPS_FILE = "full-aa.txt"
MALICIOUS_IPS = set()
LAST_MALICIOUS_LINES = []

os.makedirs(CAPTURES_DIR, exist_ok=True)

SUSPICIOUS_KEYWORDS = {'minerd', 'xmrig', 'tor', 'ngrok', 'ssh', 'perl', 'sh', 'bash', 'nc', 'netcat'}
SUSPICIOUS_PORTS = {'22', '23', '31337', '6667', '4444', '5555'}

def extract_ip(addr_str):
    if not addr_str or addr_str == "N/A":
        return None
    return addr_str.split(':')[0]

def load_malicious_ips(filepath=MALICIOUS_IPS_FILE):
    global MALICIOUS_IPS, LAST_MALICIOUS_LINES
    try:
        with open(filepath, "r") as f:
            lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        MALICIOUS_IPS = set(lines)
        LAST_MALICIOUS_LINES = lines[-10:]
        print(f"[+] {len(MALICIOUS_IPS)} IPs malveillantes chargées.")
    except FileNotFoundError:
        print(f"[!] Fichier {filepath} non trouvé.")
        MALICIOUS_IPS = set()
        LAST_MALICIOUS_LINES = []

def update_malicious_ips_periodically():
    while True:
        try:
            print("[🔄] Mise à jour de full-aa.txt...")
            url = "https://raw.githubusercontent.com/romainmarcoux/malicious-ip/master/full-aa.txt"
            urllib.request.urlretrieve(url, MALICIOUS_IPS_FILE)
            load_malicious_ips()
        except Exception as e:
            print(f"[!] Erreur : {e}")
        time.sleep(3600)

def get_process_name(pid):
    if pid is None:
        return "System"
    try:
        return psutil.Process(pid).name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return f"[PID {pid} - inaccessible]"

def safe_addr(addr):
    if not addr or not isinstance(addr, (tuple, list)):
        return "N/A"
    if len(addr) == 0:
        return "N/A"
    if len(addr) == 1:
        return str(addr[0])
    return f"{addr[0]}:{addr[1]}"

def get_connections():
    conns = []
    try:
        for c in psutil.net_connections(kind='inet'):
            pid = c.pid
            process = get_process_name(pid)
            protocol = "TCP" if c.type == socket.SOCK_STREAM else "UDP" if c.type == socket.SOCK_DGRAM else "Other"
            laddr = safe_addr(c.laddr)
            raddr = safe_addr(c.raddr)
            status = getattr(c, 'status', 'N/A')
            family = "IPv4" if c.family == socket.AF_INET else "IPv6" if c.family == socket.AF_INET6 else "Other"
            conns.append({
                "pid": pid,
                "process": process,
                "protocol": protocol,
                "local_address": laddr,
                "remote_address": raddr,
                "status": status,
                "family": family
            })
    except psutil.AccessDenied:
        return [{"error": "Accès refusé. Relancez avec sudo pour voir les processus."}]
    return conns

def is_suspicious(conn):
    proc = conn.get("process", "").lower()
    if any(kw in proc for kw in SUSPICIOUS_KEYWORDS):
        return True
    raddr = conn.get("remote_address", "")
    if ":" in raddr:
        port = raddr.split(":")[-1]
        if port in SUSPICIOUS_PORTS:
            return True
    # ✅ Vérification en SOURCE ET DESTINATION
    src_ip = extract_ip(conn.get("local_address"))
    dst_ip = extract_ip(conn.get("remote_address"))
    if (src_ip and src_ip in MALICIOUS_IPS) or (dst_ip and dst_ip in MALICIOUS_IPS):
        return True
    return False

# === Routes ===
@app.route('/')
def index():
    captures = sorted(os.listdir(CAPTURES_DIR), reverse=True)
    return render_template('index.html', captures=captures)

@app.route('/api/connections')
def api_connections():
    conns = get_connections()
    for c in conns:
        if not c.get("error"):
            c["suspicious"] = is_suspicious(c)
    return jsonify(conns)

@app.route('/api/alerts')
def api_alerts():
    conns = get_connections()
    return jsonify([c for c in conns if not c.get("error") and is_suspicious(c)])

@app.route('/api/malicious-ips')
def api_malicious_ips():
    return jsonify({
        "count": len(MALICIOUS_IPS),
        "ips": sorted(MALICIOUS_IPS),
        "last_added": LAST_MALICIOUS_LINES
    })

@app.route('/api/reload-malicious-ips', methods=['POST'])
def api_reload_malicious_ips():
    load_malicious_ips()
    return jsonify({"status": "success", "count": len(MALICIOUS_IPS)})

@app.route('/api/save', methods=['POST'])
def api_save():
    data = request.json.get('data', [])
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"capture-{timestamp}.json"
    filepath = os.path.join(CAPTURES_DIR, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=2)
    return jsonify({"filename": filename})

@app.route('/api/captures')
def api_captures():
    return jsonify(sorted(os.listdir(CAPTURES_DIR), reverse=True))

@app.route('/api/load/<filename>')
def api_load(filename):
    filepath = os.path.join(CAPTURES_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Fichier non trouvé"}), 404
    with open(filepath, 'r') as f:
        return jsonify(json.load(f))

load_malicious_ips()
threading.Thread(target=update_malicious_ips_periodically, daemon=True).start()

if __name__ == '__main__':
    print("🚀 Network Forensic Monitor démarré sur http://localhost:11111")
    print("ℹ️  Utilisez sudo pour voir tous les processus.")
    app.run(host='127.0.0.1', port=11111, debug=False, use_reloader=False)