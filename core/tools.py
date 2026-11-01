import os
import subprocess
import datetime
import platform
import shutil
import socket
import urllib.request
import json

# Railway High-Speed VPS Configuration (48 CPU Cores, 512GB RAM, 2.9TB SSD)
VPS_HOST = os.getenv("VPS_HOST", "iriguchi.proxy.rlwy.net")
VPS_PORT = int(os.getenv("VPS_PORT", "58259"))
VPS_USER = os.getenv("VPS_USER", "ajit")
VPS_PASS = os.getenv("VPS_PASS", "ajit1234")

def is_running_on_vps() -> bool:
    """Checks if current execution environment is already the Railway VPS."""
    try:
        import getpass
        node = platform.node()
        user = getpass.getuser()
        if user == "ajit" or "c77b48aac227" in node:
            return True
    except Exception:
        pass
    return False

def get_system_status():
    """Returns basic system diagnostics (CPU, Memory, Uptime, OS)."""
    return get_detailed_sysinfo()

def get_detailed_sysinfo():
    """Returns live hardware specs, RAM, CPU cores, Disk, and Kernel from the Railway VPS."""
    # Run diagnostics on the Railway VPS directly
    out = run_safe_shell_command("uname -s -r -m && lscpu | grep 'Model name\\|CPU(s):' && free -h && df -h /")
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return {
        "status": "online",
        "current_time": now,
        "vps_target": f"{VPS_USER}@{VPS_HOST}:{VPS_PORT}",
        "vps_specs": "48 CPU Cores (AMD EPYC 9655P), 512GB RAM, 2.9TB NVMe Storage, Debian Linux",
        "live_telemetry": out
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

def run_safe_shell_command(cmd: str) -> str:
    """
    Executes a shell command directly on the Railway VPS (48-Core, 512GB RAM).
    If running locally on the VPS, runs via subprocess.
    If running on Vercel or any external host, runs via SSH (iriguchi.proxy.rlwy.net:58259).
    """
    cmd_clean = cmd.strip()
    cmd_lower = cmd_clean.lower()
    blocked = ["rm -rf /", "rm -rf ~", "mkfs", ":(){ :|:& };:", "dd if=/dev/zero", "shutdown", "reboot", "init 0"]
    for b in blocked:
        if b in cmd_lower:
            return f"Command '{cmd_clean}' blocked for system safety."

    # 1. If currently running directly on the Railway VPS, execute locally for sub-millisecond response
    if is_running_on_vps():
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
            return f"Error executing locally on VPS: {str(e)}"

    # 2. If running remotely (e.g. Vercel serverless), execute via SSH on the Railway VPS
    try:
        import paramiko
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(VPS_HOST, port=VPS_PORT, username=VPS_USER, password=VPS_PASS, timeout=8)
        stdin, stdout, stderr = ssh.exec_command(cmd_clean, timeout=12)
        out = (stdout.read().decode("utf-8", errors="replace") + stderr.read().decode("utf-8", errors="replace")).strip()
        ssh.close()
        if not out:
            return "(Command completed on Railway VPS with return code 0 and no output)"
        if len(out) > 1200:
            out = out[:1200] + "\n... [Output truncated for brevity]"
        return out
    except Exception as e:
        # Fallback to local subprocess if remote SSH fails
        try:
            res = subprocess.run(cmd_clean, shell=True, capture_output=True, text=True, timeout=10)
            return (res.stdout + res.stderr).strip() or "(Executed locally)"
        except Exception as ex:
            return f"Error executing command: SSH failed ({str(e)}), Local failed ({str(ex)})"

def clean_system_cache():
    """Safely purges temporary files and system caches on the Railway VPS."""
    cmd = "pip cache purge && rm -rf /tmp/*.tmp /tmp/pip-*"
    out = run_safe_shell_command(cmd)
    return [out]

PARALLEL_API_KEY = os.getenv("PARALLEL_API_KEY", os.getenv("WEB_SEARCH_KEY", "fe55PTLHGgIjHGiWvx1KkIZNNAix__3IQraBtDkX"))

def search_parallel_ai(query: str, max_results: int = 4) -> str:
    """Performs real-time web search using Parallel AI (Parallel Web API)."""
    clean_q = query.strip()
    if not clean_q or not PARALLEL_API_KEY:
        return ""
    try:
        import urllib.request
        req_body = json.dumps({
            "objective": f"Search and summarize real-time web information for: {clean_q}",
            "search_queries": [clean_q]
        }).encode("utf-8")

        req = urllib.request.Request(
            "https://api.parallel.ai/v1/search",
            data=req_body,
            headers={
                "Content-Type": "application/json",
                "x-api-key": PARALLEL_API_KEY
            }
        )
        with urllib.request.urlopen(req, timeout=4) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            snippets = []
            for r in results[:max_results]:
                title = r.get("title", "").strip()
                excerpts = r.get("excerpts", [])
                excerpt_text = " ".join(excerpts).replace("\n", " ").strip()
                if len(excerpt_text) > 300:
                    excerpt_text = excerpt_text[:300] + "..."
                if title and excerpt_text:
                    snippets.append(f"• {title}: {excerpt_text}")
            return "\n".join(snippets) if snippets else ""
    except Exception as e:
        print(f"[Parallel AI Search Error] {e}")
        return ""

def search_web(query: str, max_results: int = 4) -> str:
    """Performs live web search using Parallel AI (Parallel Web) with DuckDuckGo fallback."""
    clean_q = query.strip()
    if not clean_q:
        return "Empty query provided."

    # 1. Primary: Parallel AI Real-time Web Search
    parallel_res = search_parallel_ai(clean_q, max_results=max_results)
    if parallel_res.strip():
        return parallel_res

    # 2. Resilient Fallback: DuckDuckGo Search
    try:
        try:
            from ddgs import DDGS
        except ImportError:
            from duckduckgo_search import DDGS

        results = list(DDGS().text(clean_q, max_results=max_results))
        if not results:
            return "No web results found."

        snippets = []
        for i, r in enumerate(results, 1):
            title = r.get("title", "").strip()
            body = r.get("body", "").strip()
            if title and body:
                snippets.append(f"• {title}: {body}")

        return "\n".join(snippets) if snippets else "No web results found."
    except Exception as e:
        return f"Web search error: {str(e)}"
