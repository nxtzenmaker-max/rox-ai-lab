# ⚡ ROX LAB - Hacker & Developer Multi-Tool Terminal Suite

A modular, standalone, cyberpunk-themed **Multi-Tool Terminal Lab & Operating Console** for developers, pentesters, and power users. 100% offline capable with zero external API dependencies required for core tools.

---

## 🛠️ Built-in Terminal Tools

| Command | Category | Description |
| :--- | :--- | :--- |
| **`ip`** | Network Recon | Local & Public IP, Country, City, and ISP / Organization lookup |
| **`scan <host> [ports]`** | Network Recon | Fast multi-threaded TCP Port Scanner with service detection |
| **`headers <url>`** | Web Recon | Inspect HTTP response headers and security configs |
| **`hash <text>`** | Cryptography | Instant MD5, SHA1, SHA256, SHA512 hash generator |
| **`b64enc <text>`** | Cryptography | Base64 encode string |
| **`b64dec <string>`** | Cryptography | Base64 decode string |
| **`genpass [len]`** | Cryptography | Generate cryptographically secure passwords & tokens |
| **`hex <text>`** | Cryptography | Text to Hex and Hex to Text converter |
| **`sys`** | System | Detailed hardware metrics (CPU cores, RAM, Disk, OS) |
| **`clean`** | Maintenance | Purge temporary files and caches safely |
| **`tunnel <port>`** | Connectivity | 1-Click Cloudflare public tunnel for any local port |
| **`share [dir] [port]`** | Sharing | Instant HTTP file sharing server |
| **`custom`** | Extensibility | Interactive launcher for scripts inside `custom_tools/` |
| **`<any bash cmd>`** | Shell | Native pass-through for bash commands (`ls`, `git`, `htop`, etc.) |

---

## 🚀 Quick Start

Run the terminal suite directly:
```bash
rox
```
*(or run `./venv/bin/python3 lab.py`)*

### Adding Your Own Tools:
Drop any `.sh` or `.py` scripts inside the `custom_tools/` folder. They will automatically appear when you type `custom` in the terminal!

---

## 🌟 Optional Standalone Modules
- **3D Humanoid Avatar (Web UI)**: Run `python3 server.py` and open the Three.js avatar in browser.
- **Twilio Phone Calling Agent**: Integrated WebSocket voice engine on `/twilio/stream`.
