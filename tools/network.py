import socket
import urllib.request
import json
import concurrent.futures

def get_ip_info():
    """Returns local and public IP info with Geo data."""
    info = {}
    
    # Local IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["local_ip"] = s.getsockname()[0]
        s.close()
    except Exception:
        info["local_ip"] = "127.0.0.1"

    # Public IP & Geo
    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode())
            info["public_ip"] = data.get("query", "Unknown")
            info["country"] = data.get("country", "Unknown")
            info["city"] = data.get("city", "Unknown")
            info["isp"] = data.get("isp", "Unknown")
            info["org"] = data.get("org", "Unknown")
    except Exception:
        info["public_ip"] = "Unavailable"
        info["country"] = "Unavailable"
        info["city"] = "Unavailable"
        info["isp"] = "Unavailable"
        info["org"] = "Unavailable"

    return info

def scan_port(host, port, timeout=1.0):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except Exception:
                service = "unknown"
            return (port, True, service)
    except Exception:
        pass
    return (port, False, "")

def run_port_scan(host, ports=None):
    """Scans common or specified ports concurrently."""
    if not ports:
        ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 465, 587, 993, 995, 1433, 3306, 3389, 5432, 6379, 8000, 8080, 8443, 8888, 9000, 27017]
    
    open_ports = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        futures = [executor.submit(scan_port, host, p) for p in ports]
        for f in concurrent.futures.as_completed(futures):
            port, is_open, service = f.result()
            if is_open:
                open_ports.append((port, service))
    
    open_ports.sort(key=lambda x: x[0])
    return open_ports

def check_http_headers(url):
    """Fetches and returns HTTP headers for security / tech inspection."""
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
    with urllib.request.urlopen(req, timeout=6) as resp:
        return dict(resp.headers)
