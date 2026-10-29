import os
import sys
import subprocess
import time
import datetime
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown
from rich.text import Text
from rich.live import Live
from rich.prompt import Prompt
from dotenv import load_dotenv

load_dotenv()

from core.brain import get_ai_response
from core.tools import get_system_status, run_safe_shell_command
from core.voice import generate_speech

console = Console()

BANNER = """[bold cyan]
 ██████╗  ██████╗ ██╗  ██╗    ██╗      █████╗ ██████╗ 
 ██╔══██╗██╔═══██╗╚██╗██╔╝    ██║     ██╔══██╗██╔══██╗
 ██████╔╝██║   ██║ ╚███╔╝     ██║     ███████║██████╔╝
 ██╔══██╗██║   ██║ ██╔██╗     ██║     ██╔══██║██╔══██╗
 ██║  ██║╚██████╔╝██╔╝ ██╗    ███████╗██║  ██║██████╔╝
 ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝    ╚══════╝╚═╝  ╚═╝╚═════╝ 
[/bold cyan][bold magenta]        ⚡ NEURAL AGENT LAB & OPERATING CONSOLE ⚡[/bold magenta]
"""

class RoxLab:
    def __init__(self):
        self.history = []
        self.voice_enabled = False
        self.server_process = None
        self.tunnel_process = None

    def print_banner(self):
        console.clear()
        console.print(BANNER)
        
        # Info Table
        table = Table(show_header=False, box=None, padding=(0, 2))
        table.add_row("[bold green]● IDENTITY:[/bold green]", "[white]ROX (RJN) - Cybernetic Pair Programmer[/white]")
        table.add_row("[bold cyan]● LLM BRAIN:[/bold cyan]", f"[cyan]{os.getenv('GROQ_MODEL', 'openai/gpt-oss-120b')} [ONLINE][/cyan]")
        table.add_row("[bold yellow]● VOICE CORE:[/bold yellow]", f"[yellow]{os.getenv('DEEPGRAM_VOICE', 'aura-orion-en')} / Edge-TTS[/yellow]")
        table.add_row("[bold magenta]● PHONE LINK:[/bold magenta]", "[magenta]Twilio WebSocket Gateway [READY][/magenta]")
        
        console.print(Panel(table, border_style="cyan", title="[bold white]SYSTEM METRICS[/bold white]", subtitle="[dim]Type /help for commands[/dim]"))
        console.print()

    def show_help(self):
        table = Table(title="🔧 ROX COMMAND MATRIX", border_style="cyan")
        table.add_column("Command", style="bold magenta", no_wrap=True)
        table.add_column("Description", style="white")
        table.add_row("/status", "System resources (RAM, CPU, Disk, Time)")
        table.add_row("/3d", "Start 3D Humanoid Web Server & Cloudflare Tunnel")
        table.add_row("/voice on|off", "Toggle voice output in terminal")
        table.add_row("/sh <cmd>", "Run local bash command inside lab")
        table.add_row("/clear", "Clear screen and redisplay banner")
        table.add_row("/exit, exit", "Exit Rox Lab")
        console.print(table)

    def print_status(self):
        diag = get_system_status()
        table = Table(title="📊 HOST SYSTEM DIAGNOSTICS", border_style="green")
        table.add_column("Parameter", style="cyan")
        table.add_column("Value", style="green")
        for k, v in diag.items():
            table.add_row(k.replace("_", " ").title(), str(v))
        console.print(table)

    def run_bash(self, cmd: str):
        console.print(f"[dim yellow]⚡ Executing:[/dim yellow] [bold]{cmd}[/bold]")
        out = run_safe_shell_command(cmd)
        console.print(Panel(out, border_style="yellow", title="BASH OUTPUT"))

    def toggle_voice(self, arg: str):
        if "on" in arg.lower():
            self.voice_enabled = True
            console.print("[green]🔊 Voice mode ENABLED. Rox will speak replies![/green]")
        else:
            self.voice_enabled = False
            console.print("[yellow]🔇 Voice mode DISABLED. Terminal silent mode.[/yellow]")

    def launch_3d_server(self):
        console.print("[bold cyan]🚀 Starting 3D Humanoid Server in background...[/bold cyan]")
        try:
            # Check if running
            res = subprocess.run("pgrep -f 'uvicorn server:app'", shell=True, capture_output=True)
            if res.returncode == 0:
                console.print("[yellow]ℹ️ Server is already running on port 8000![/yellow]")
            else:
                subprocess.Popen([sys.executable, "-m", "uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"],
                                 stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                console.print("[green]✅ Server started on http://localhost:8000[/green]")

            # Tunnel
            if os.path.exists("/home/ipx/cloudflared"):
                console.print("[dim cyan]Starting Cloudflare tunnel... Link will generate below:[/dim cyan]")
                subprocess.Popen(["/home/ipx/cloudflared", "tunnel", "--url", "http://localhost:8000"])
            else:
                console.print("[cyan]Open in browser: http://localhost:8000[/cyan]")
        except Exception as e:
            console.print(f"[red]Error starting server: {e}[/red]")

    def chat(self, user_msg: str):
        with console.status("[bold cyan]Rox is processing...[/bold cyan]", spinner="dots"):
            reply = get_ai_response(user_msg, self.history)
            self.history.append({"role": "user", "content": user_msg})
            self.history.append({"role": "assistant", "content": reply})

        console.print()
        console.print(Panel(Markdown(reply), border_style="cyan", title="[bold magenta]ROX (RJN)[/bold magenta]"))
        console.print()

        if self.voice_enabled:
            # Play speech in background if audio player exists
            try:
                audio_bytes = asyncio.run(generate_speech(reply))
                with open("/tmp/rox_speech.mp3", "wb") as f:
                    f.write(audio_bytes)
                subprocess.Popen(["mpv", "--no-terminal", "/tmp/rox_speech.mp3"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            except Exception:
                pass

    def run(self):
        self.print_banner()

        while True:
            try:
                prompt_text = "[bold cyan]╭─[[bold green]rox@lab[/bold green]]─[[white]~[/white]]\n╰─► [/bold cyan]"
                user_input = Prompt.ask(prompt_text).strip()

                if not user_input:
                    continue

                if user_input.lower() in ["exit", "quit", "/exit"]:
                    console.print("[bold cyan]Alvida bhai! Rox shutting down... ⚡[/bold cyan]")
                    break
                elif user_input == "/clear":
                    self.print_banner()
                elif user_input == "/help":
                    self.show_help()
                elif user_input == "/status":
                    self.print_status()
                elif user_input == "/3d":
                    self.launch_3d_server()
                elif user_input.startswith("/voice"):
                    self.toggle_voice(user_input)
                elif user_input.startswith("/sh "):
                    self.run_bash(user_input[4:])
                else:
                    self.chat(user_input)

            except (KeyboardInterrupt, EOFError):
                console.print("\n[bold cyan]Session closed. See you bhai! ⚡[/bold cyan]")
                break

if __name__ == "__main__":
    lab = RoxLab()
    lab.run()
