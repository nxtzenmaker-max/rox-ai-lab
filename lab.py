import os
import sys
import subprocess
import shlex
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

# Import Modular Toolkits
from tools.network import get_ip_info, run_port_scan, check_http_headers
from tools.crypto_sec import get_hashes, b64_encode, b64_decode, generate_strong_password, hex_encode, hex_decode
from tools.system import get_detailed_sysinfo, clean_system
from tools.tunnel import start_tunnel, start_file_server

console = Console()

BANNER = """[bold cyan]
  ___  _____  __  _____ ___ ___ __  __ 
 | _ \/ _ \ \/ / |_   _| __| _ \  \/  |
 |   / (_) >  <    | | | _||   / |\/| |
 |_|_\\___/_/\_\   |_| |___|_|_\\_|  |_|
[/bold cyan][bold magenta]  ⚡ MULTI-TOOL LAB & TERMINAL SUITE ⚡[/bold magenta]
"""

class RoxTerminal:
    def __init__(self):
        self.active_processes = []

    def print_banner(self):
        console.clear()
        console.print(BANNER)
        
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[bold green]● LAB STATUS:[/bold green]", "[white]READY & STANDALONE (100% Offline Capable)[/white]")
        table.add_row("[bold cyan]● TOOL MODULES:[/bold cyan]", "[cyan]Network Recon, Crypto/Hashes, SysInfo, Tunnels, Custom Scripts[/cyan]")
        table.add_row("[bold yellow]● RUNTIME:[/bold yellow]", f"[yellow]Python {sys.version.split()[0]} on Linux[/yellow]")
        
        console.print(Panel(table, border_style="cyan", title="[bold white]ROX LAB MATRIX[/bold white]", subtitle="[dim]Type 'help' or 'menu' for tools[/dim]"))
        console.print()

    def show_help(self):
        table = Table(title="🛠️ ROX MULTI-TOOL SUITE - COMMAND CHEATSHEET", border_style="cyan")
        table.add_column("Command", style="bold magenta", no_wrap=True)
        table.add_column("Category", style="cyan")
        table.add_column("Description", style="white")

        # Network
        table.add_row("ip", "Network", "Get local IP, public IP, ISP & Country info")
        table.add_row("scan <host> [ports]", "Network", "Fast multi-threaded TCP Port Scanner")
        table.add_row("headers <url>", "Network", "Inspect HTTP response headers of a website")

        # Crypto & Hashes
        table.add_row("hash <text>", "Crypto", "Generate MD5, SHA1, SHA256, SHA512 hashes")
        table.add_row("b64enc <text>", "Crypto", "Base64 encode a string")
        table.add_row("b64dec <string>", "Crypto", "Base64 decode a string")
        table.add_row("genpass [length]", "Crypto", "Generate cryptographically secure password")
        table.add_row("hex <text>", "Crypto", "Convert string to hex / hex to string")

        # System
        table.add_row("sys", "System", "Full hardware specs, RAM, CPU cores, Disk")
        table.add_row("clean", "System", "Safely clean temporary files and caches")

        # Sharing & Tunnels
        table.add_row("tunnel <port>", "Tunnel", "Start 1-click Cloudflare tunnel for local port")
        table.add_row("share [dir] [port]", "Sharing", "Instant HTTP file server for directory sharing")

        # Custom & Terminal
        table.add_row("custom", "Custom", "List and run scripts in custom_tools/ folder")
        table.add_row("<any bash cmd>", "Shell", "Runs standard bash commands directly (e.g. ls, git, ping)")
        table.add_row("clear", "Terminal", "Clear terminal screen and redraw banner")
        table.add_row("exit", "Terminal", "Exit Rox Terminal Lab")

        console.print(table)

    def handle_ip(self):
        with console.status("[cyan]Fetching IP and Geo info...[/cyan]"):
            data = get_ip_info()
        t = Table(title="🌐 IP & NETWORK INFO", border_style="green")
        t.add_column("Key", style="bold cyan")
        t.add_column("Value", style="bold green")
        for k, v in data.items():
            t.add_row(k.replace("_", " ").title(), str(v))
        console.print(t)

    def handle_scan(self, args):
        if not args:
            console.print("[red]Usage: scan <host> [port1,port2,...][/red]")
            return
        parts = args.split()
        host = parts[0]
        custom_ports = None
        if len(parts) > 1:
            try:
                custom_ports = [int(p) for p in parts[1].split(",")]
            except ValueError:
                console.print("[red]Invalid ports format. Example: scan 127.0.0.1 22,80,443[/red]")
                return

        console.print(f"[bold cyan]🔍 Scanning {host}...[/bold cyan]")
        with console.status("[cyan]Scanning open ports...[/cyan]", spinner="bouncingBar"):
            open_ports = run_port_scan(host, custom_ports)

        if open_ports:
            t = Table(title=f"🔓 OPEN PORTS ON {host.upper()}", border_style="green")
            t.add_column("Port", style="bold magenta")
            t.add_column("Service", style="bold green")
            for p, s in open_ports:
                t.add_row(str(p), s.upper())
            console.print(t)
        else:
            console.print(f"[yellow]No open ports discovered on {host}.[/yellow]")

    def handle_headers(self, url):
        if not url:
            console.print("[red]Usage: headers <url>[/red]")
            return
        try:
            with console.status("[cyan]Connecting and fetching headers...[/cyan]"):
                hdrs = check_http_headers(url)
            t = Table(title=f"📋 HTTP HEADERS: {url}", border_style="cyan")
            t.add_column("Header", style="bold cyan")
            t.add_column("Value", style="white")
            for k, v in hdrs.items():
                t.add_row(k, v)
            console.print(t)
        except Exception as e:
            console.print(f"[red]Error fetching headers: {e}[/red]")

    def handle_hash(self, text):
        if not text:
            console.print("[red]Usage: hash <text>[/red]")
            return
        res = get_hashes(text)
        t = Table(title=f"🔐 CRYPTOGRAPHIC HASHES FOR: '{text}'", border_style="magenta")
        t.add_column("Algorithm", style="bold cyan")
        t.add_column("Hash Digest", style="bold yellow")
        for k, v in res.items():
            t.add_row(k, v)
        console.print(t)

    def handle_sys(self):
        info = get_detailed_sysinfo()
        t = Table(title="🖥️ HOST HARDWARE & SYSTEM SPECS", border_style="green")
        t.add_column("Component", style="bold cyan")
        t.add_column("Details", style="bold green")
        for k, v in info.items():
            t.add_row(k, str(v))
        console.print(t)

    def handle_clean(self):
        with console.status("[cyan]Cleaning temporary caches...[/cyan]"):
            logs = clean_system()
        t = Table(title="🧹 SYSTEM CLEANUP REPORT", border_style="green")
        t.add_column("Action Log", style="white")
        for log in logs:
            t.add_row(log)
        console.print(t)

    def handle_tunnel(self, port_str):
        if not port_str:
            console.print("[red]Usage: tunnel <port>[/red]")
            return
        try:
            port = int(port_str.strip())
            console.print(f"[bold cyan]🌐 Initializing Cloudflare tunnel on port {port}...[/bold cyan]")
            ok, proc_or_err = start_tunnel(port)
            if not ok:
                console.print(f"[red]{proc_or_err}[/red]")
            else:
                self.active_processes.append(proc_or_err)
                console.print("[green]Tunnel process started in background.[/green]")
        except ValueError:
            console.print("[red]Port must be a valid integer.[/red]")

    def handle_share(self, args):
        parts = args.split()
        directory = parts[0] if len(parts) > 0 else os.getcwd()
        port = int(parts[1]) if len(parts) > 1 else 8080

        console.print(f"[bold cyan]📁 Sharing '{directory}' on port {port}...[/bold cyan]")
        ok, proc = start_file_server(directory, port)
        if ok:
            self.active_processes.append(proc)
            console.print(f"[bold green]✅ Local File Server active: http://localhost:{port}[/bold green]")
            console.print(f"[dim]Tip: Run 'tunnel {port}' to get a public link for mobile sharing![/dim]")
        else:
            console.print(f"[red]{proc}[/red]")

    def handle_custom(self):
        custom_dir = os.path.join(os.path.dirname(__file__), "custom_tools")
        if not os.path.exists(custom_dir):
            os.makedirs(custom_dir)
        scripts = [f for f in os.listdir(custom_dir) if os.path.isfile(os.path.join(custom_dir, f))]
        
        if not scripts:
            console.print(f"[yellow]No custom scripts found in '{custom_dir}'. Add .sh or .py scripts there![/yellow]")
            return

        t = Table(title="⚡ CUSTOM USER TOOLS", border_style="magenta")
        t.add_column("#", style="bold cyan")
        t.add_column("Script Name", style="bold green")
        for idx, s in enumerate(scripts, 1):
            t.add_row(str(idx), s)
        console.print(t)

        choice = Prompt.ask("[cyan]Enter script number to execute (or Enter to cancel)[/cyan]", default="")
        if choice.isdigit() and 1 <= int(choice) <= len(scripts):
            target = os.path.join(custom_dir, scripts[int(choice) - 1])
            console.print(f"[bold yellow]Running {scripts[int(choice) - 1]}...[/bold yellow]")
            subprocess.run(target if os.access(target, os.X_OK) else f"bash {target}", shell=True)

    def execute_shell(self, cmd):
        """Pass through to system bash shell."""
        try:
            subprocess.run(cmd, shell=True)
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")

    def run(self):
        self.print_banner()

        while True:
            try:
                prompt_str = "[bold cyan]╭─[[bold green]rox@lab[/bold green]]─[[white]tools[/white]]\n╰─► [/bold cyan]"
                raw_input = Prompt.ask(prompt_str).strip()

                if not raw_input:
                    continue

                parts = raw_input.split(maxsplit=1)
                cmd = parts[0].lower()
                arg = parts[1] if len(parts) > 1 else ""

                if cmd in ["exit", "quit", "q"]:
                    console.print("[bold cyan]Exiting Rox Terminal Lab. Have fun![/bold cyan]")
                    for p in self.active_processes:
                        p.terminate()
                    break

                elif cmd in ["help", "menu", "?", "tools"]:
                    self.show_help()

                elif cmd in ["clear", "cls"]:
                    self.print_banner()

                elif cmd == "ip":
                    self.handle_ip()

                elif cmd == "scan":
                    self.handle_scan(arg)

                elif cmd == "headers":
                    self.handle_headers(arg)

                elif cmd == "hash":
                    self.handle_hash(arg)

                elif cmd == "b64enc":
                    console.print(f"[bold yellow]Base64:[/bold yellow] [green]{b64_encode(arg)}[/green]")

                elif cmd == "b64dec":
                    console.print(f"[bold yellow]Decoded:[/bold yellow] [green]{b64_decode(arg)}[/green]")

                elif cmd == "genpass":
                    length = int(arg) if arg.isdigit() else 16
                    console.print(f"[bold yellow]Strong Password ({length} chars):[/bold yellow] [bold green]{generate_strong_password(length)}[/bold green]")

                elif cmd == "hex":
                    console.print(f"[bold yellow]Hex:[/bold yellow] [green]{hex_encode(arg)}[/green]")

                elif cmd == "sys":
                    self.handle_sys()

                elif cmd == "clean":
                    self.handle_clean()

                elif cmd == "tunnel":
                    self.handle_tunnel(arg)

                elif cmd == "share":
                    self.handle_share(arg)

                elif cmd == "custom":
                    self.handle_custom()

                else:
                    # Direct shell command execution
                    self.execute_shell(raw_input)

            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold cyan]Terminal session closed.[/bold cyan]")
                break

if __name__ == "__main__":
    app = RoxTerminal()
    app.run()
