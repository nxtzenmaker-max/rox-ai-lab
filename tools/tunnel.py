import os
import subprocess
import sys

def get_cloudflared_path():
    if os.path.exists("/home/ipx/cloudflared"):
        return "/home/ipx/cloudflared"
    res = subprocess.run("which cloudflared", shell=True, capture_output=True, text=True)
    if res.returncode == 0:
        return res.stdout.strip()
    return None

def start_tunnel(port: int):
    bin_path = get_cloudflared_path()
    if not bin_path:
        return False, "cloudflared binary not found! Please place it in PATH or /home/ipx/cloudflared."
    
    cmd = [bin_path, "tunnel", "--url", f"http://localhost:{port}"]
    proc = subprocess.Popen(cmd)
    return True, proc

def start_file_server(directory: str, port: int = 8080):
    if not os.path.exists(directory):
        return False, f"Directory '{directory}' does not exist."
    
    cmd = [sys.executable, "-m", "http.server", str(port), "--directory", directory]
    proc = subprocess.Popen(cmd)
    return True, proc
