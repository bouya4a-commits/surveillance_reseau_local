# network_monitor.py
import psutil
import socket
from flask import Flask, jsonify
import logging

# Désactiver les logs Flask par défaut pour plus de clarté
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

app = Flask(__name__)

def get_process_name(pid):
    """Récupère le nom du processus à partir du PID, en gérant les erreurs."""
    if pid is None:
        return "System"
    try:
        proc = psutil.Process(pid)
        return proc.name()
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        return f"[PID {pid} - inaccessible]"

def get_protocol_name(family, type_):
    """Détermine le protocole (TCP/UDP) à partir de la famille et du type."""
    if family == socket.AF_INET or family == socket.AF_INET6:
        if type_ == socket.SOCK_STREAM:
            return "TCP"
        elif type_ == socket.SOCK_DGRAM:
            return "UDP"
    return "Other"

def safe_addr(addr):
    """Convertit une adresse (ip, port) en chaîne, gère les None."""
    if addr is None:
        return "N/A"
    ip, port = addr
    return f"{ip}:{port}"

def get_connections():
    """Récupère les connexions réseau actives de manière sécurisée."""
    connections = []
    try:
        conns = psutil.net_connections(kind='inet')
    except psutil.AccessDenied:
        # Sur macOS, certaines connexions nécessitent des droits élevés
        return [{"error": "Accès refusé. Essayez avec 'sudo' pour plus de détails."}]

    for conn in conns:
        try:
            pid = conn.pid
            process_name = get_process_name(pid)
            protocol = get_protocol_name(conn.family, conn.type)
            laddr = safe_addr(conn.laddr)
            raddr = safe_addr(conn.raddr)
            status = conn.status if hasattr(conn, 'status') and conn.status else "N/A"
            family_str = "IPv4" if conn.family == socket.AF_INET else "IPv6" if conn.family == socket.AF_INET6 else "Other"

            connections.append({
                "pid": pid,
                "process": process_name,
                "protocol": protocol,
                "local_address": laddr,
                "remote_address": raddr,
                "status": status,
                "family": family_str
            })
        except Exception as e:
            # Log silencieux ou ajout d'une entrée d'erreur (optionnel)
            continue  # Ignore les connexions corrompues ou obsolètes
    return connections

@app.route('/connections', methods=['GET'])
def connections_endpoint():
    try:
        conns = get_connections()
        return jsonify(conns)
    except Exception as e:
        return jsonify({"error": "Internal error", "details": str(e)}), 500

@app.route('/', methods=['GET'])
def home():
    return """
    <h1>🔍 Network Forensic Monitor (macOS)</h1>
    <p>Accédez aux connexions actives : <a href="/connections">/connections</a></p>
    <p><i>Conseil : Si les processus sont masqués, relancez avec <code>sudo python3 network_monitor.py</code></i></p>
    """

if __name__ == '__main__':
    print("🚀 Démarrage du moniteur réseau sur http://localhost:11111")
    print("ℹ️  Sur macOS, certaines infos nécessitent des droits admin (sudo).")
    app.run(host='127.0.0.1', port=11111, debug=False, use_reloader=False)
