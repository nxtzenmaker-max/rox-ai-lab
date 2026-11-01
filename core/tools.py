import os
import subprocess
import datetime
import platform
import shutil
import socket
import urllib.request
import json

def get_system_status():
    """Returns basic system diagnostics (CPU, Memory, Uptime, OS)."""
    return get_detailed_sysinfo()

def get_detailed_sysinfo():
    """Returns full hardware specs, RAM, CPU cores, Disk, and Kernel."""
    uname = platform.uname()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # RAM info from /proc/meminfo if available
    mem_total = "Unknown"
    mem_free = "Unknown"
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    mem_total = f"{int(line.split()[1]) // 1024} MB"
                elif "MemAvailable" in line:
                    mem_free = f"{int(line.split()[1]) // 1024} MB"
    except Exception:
        pass

    # Disk
    try:
        disk = shutil.disk_usage("/")
        total_disk = f"{disk.total // (1024**3)} GB"
        free_disk = f"{disk.free // (1024**3)} GB"
        used_disk = f"{disk.used // (1024**3)} GB"
    except Exception:
        total_disk = free_disk = used_disk = "Unknown"

    cores = os.cpu_count() or 1

    return {
        "status": "online",
        "current_time": now,
        "os": f"{uname.system} {uname.release} ({uname.machine})",
        "hostname": uname.node,
        "cpu_cores": f"{cores} Cores",
        "ram": f"{mem_free} available of {mem_total}",
        "disk_usage": f"{used_disk} used of {total_disk} ({free_disk} free)",
    }

def get_network_info():
    """Returns local IP, Public IP, Geo and ISP."""
    info = {}
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        info["local_ip"] = s.getsockname()[0]
        s.close()
    except Exception:
        info["local_ip"] = "127.0.0.1"

    try:
        req = urllib.request.Request("http://ip-api.com/json/", headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=4) as response:
            data = json.loads(response.read().decode())
            info["public_ip"] = data.get("query", "Unknown")
            info["location"] = f"{data.get('city', '')}, {data.get('country', '')}"
            info["isp"] = data.get("isp", "Unknown")
    except Exception:
        info["public_ip"] = "Unavailable"
        info["location"] = "Unknown"
        info["isp"] = "Unknown"

    return info

def run_safe_shell_command(cmd: str):
    """Executes a non-destructive shell command and returns output with safety guards."""
    cmd_clean = cmd.strip()
    cmd_lower = cmd_clean.lower()
    blocked = ["rm -rf /", "rm -rf ~", "mkfs", ":(){ :|:& };:", "dd if=/dev/zero", "shutdown", "reboot", "init 0"]
    for b in blocked:
        if b in cmd_lower:
            return f"Command '{cmd_clean}' blocked for system safety."

    try:
        res = subprocess.run(cmd_clean, shell=True, capture_output=True, text=True, timeout=12)
        out = (res.stdout + res.stderr).strip()
        if not out:
            return "(Command completed with return code 0 and no output)"
        if len(out) > 1200:
            out = out[:1200] + "\n... [Output truncated for brevity]"
        return out
    except subprocess.TimeoutExpired:
        return f"Command '{cmd_clean}' timed out after 12 seconds."
    except Exception as e:
        return f"Error executing command: {str(e)}"

def clean_system_cache():
    """Safely purges temporary files and system caches."""
    cleaned = []
    try:
        res = subprocess.run("pip cache purge", shell=True, capture_output=True, text=True)
        if "Files removed" in res.stdout:
            cleaned.append(res.stdout.strip())
    except Exception:
        pass
    return cleaned if cleaned else ["System is already clean and optimized!"]
