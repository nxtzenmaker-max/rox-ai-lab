import os
import subprocess
import platform
import shutil

def get_detailed_sysinfo():
    uname = platform.uname()
    
    # RAM info from /proc/meminfo
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
    disk = shutil.disk_usage("/")
    total_disk = f"{disk.total // (1024**3)} GB"
    free_disk = f"{disk.free // (1024**3)} GB"
    used_disk = f"{disk.used // (1024**3)} GB"

    # CPU cores
    cores = os.cpu_count() or 1

    return {
        "OS / Kernel": f"{uname.system} {uname.release} ({uname.machine})",
        "Hostname": uname.node,
        "CPU Cores": str(cores),
        "Memory (RAM)": f"{mem_free} free of {mem_total}",
        "Storage (Disk)": f"{used_disk} used of {total_disk} ({free_disk} free)",
    }

def clean_system():
    """Cleans temporary files and caches safely."""
    cleaned = []
    
    # Clean /tmp user files
    tmp_cleaned = 0
    try:
        for f in os.listdir("/tmp"):
            p = os.path.join("/tmp", f)
            if os.path.isfile(p) and (f.startswith("rox_") or f.endswith(".tmp")):
                try:
                    os.remove(p)
                    tmp_cleaned += 1
                except Exception:
                    pass
        if tmp_cleaned > 0:
            cleaned.append(f"Removed {tmp_cleaned} temporary files from /tmp")
    except Exception:
        pass

    # Pip cache purge
    try:
        res = subprocess.run("pip cache purge", shell=True, capture_output=True, text=True)
        if "Files removed" in res.stdout:
            cleaned.append(res.stdout.strip())
    except Exception:
        pass

    return cleaned if cleaned else ["System is already clean! No unnecessary caches found."]
