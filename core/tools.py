import os
import subprocess
import datetime
import platform

def get_system_status():
    """Returns basic system diagnostics (CPU, Memory, Uptime, OS)."""
    uname = platform.uname()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Disk usage
    disk_stat = os.statvfs('/')
    total_gb = (disk_stat.f_blocks * disk_stat.f_frsize) / (1024**3)
    free_gb = (disk_stat.f_bfree * disk_stat.f_frsize) / (1024**3)
    used_gb = total_gb - free_gb

    return {
        "status": "online",
        "current_time": now,
        "os": f"{uname.system} {uname.release}",
        "disk_usage": f"{used_gb:.1f}GB used of {total_gb:.1f}GB ({free_gb:.1f}GB free)",
    }

def run_safe_shell_command(cmd: str):
    """Executes a non-destructive shell command and returns output."""
    cmd_lower = cmd.strip().lower()
    blocked = ["rm -rf", "mkfs", ":(){ :|:& };:", "dd if=", "shutdown", "reboot"]
    for b in blocked:
        if b in cmd_lower:
            return f"Command '{cmd}' blocked for security reasons."
            
    try:
        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        out = (res.stdout + res.stderr).strip()
        return out if out else "(Command completed with no output)"
    except Exception as e:
        return f"Error executing command: {str(e)}"
