# ⚡ ROX AI LAB - 3D Humanoid & Phone Voice Agent

An ultra-responsive **3D Humanoid AI Assistant & Autonomous Phone Agent** powered by **Groq / Llama-3**, **Deepgram Aura TTS**, and **Three.js**.

---

## 🌟 Key Features

1. **⚡ Cyberpunk Interactive Terminal Lab (`rox`)**
   - Rich terminal interface with ASCII banners, live system metrics, and markdown formatting.
   - Built-in command interpreter: `/status`, `/3d`, `/voice`, `/sh <command>`.
   - Talk and pair-program with Rox directly inside your terminal console!

2. **3D Cyber-Humanoid Avatar (Web UI)**
   - Procedural 3D metallic cyber-humanoid rig with articulated jaw.
   - Real-time vocal lip-sync driven by audio frequency analysis (FFT).
   - Audio visualizer, futuristic HUD overlay, and orbit camera controls.
   - Voice input via browser microphone (speech-to-text).

2. **Ultra-Low Latency Voice Engine**
   - **Deepgram Aura TTS** (`aura-orion-en`, `aura-helios-en`) with sub-200ms latency.
   - Automatic fallback to **Edge-TTS** (`hi-IN-MadhurNeural`) if no API key is provided.
   - Seamless speech generation for both Web (MP3) and Telephony (µ-law 8000Hz).

3. **Inbound Phone Calling Agent (Twilio Integration)**
   - Call a virtual phone number and Rox answers in real-time.
   - Bidirectional WebSocket streaming (`/twilio/stream`) with zero-transcoding overhead.
   - Takes voice commands and can execute safe shell tasks.

4. **1-Click Public Tunnel**
   - Integrated with `cloudflared` to generate instant HTTPS / WSS URLs without port forwarding or Ngrok limits.

---

## 🚀 Quick Start

### 1. Clone & Setup
```bash
git clone https://github.com/nxtzenmaker-max/rox-ai-lab.git
cd rox-ai-lab
cp .env.example .env
```

### 2. Configure Environment (`.env`)
Edit `.env` to add your keys:
```env
# Fast LLM (Required)
GROQ_API_KEY=your_groq_api_key_here

# Deepgram Aura Voice ($200 Free credits)
DEEPGRAM_API_KEY=your_deepgram_api_key_here
DEEPGRAM_VOICE=aura-orion-en

# Twilio (Optional - for Phone Agent)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
```

### 3. Launch Rox
Run the 1-click launcher:
```bash
./start.sh
```
The script will install all dependencies in a virtual environment, start the FastAPI server on port 8000, and print your public Cloudflare URL!

---

## 📞 Setting Up Twilio Phone Calls

1. In your **Twilio Console**, go to **Phone Numbers -> Manage -> Active Numbers**.
2. Select your number and scroll down to **Voice Configuration**.
3. Under **"A CALL COMES IN"**, select **Webhook** and paste your Cloudflare tunnel URL:
   ```
   https://your-tunnel-url.trycloudflare.com/twilio/incoming
   ```
   *(HTTP POST)*
4. Save settings.
5. Dial the number from any mobile phone — Rox will answer and speak with you live!

---

## 📁 Project Structure

```
rox-ai-lab/
├── core/
│   ├── brain.py       # Groq LLM reasoning & Rox persona
│   ├── voice.py       # Deepgram Aura TTS & Nova STT engine
│   └── tools.py       # Diagnostic and command execution tools
├── static/
│   ├── index.html     # 3D Humanoid Avatar interface
│   ├── style.css      # Cyberpunk Jarvis HUD styling
│   └── app.js         # Three.js rig, audio analysis & lip-sync driver
├── server.py          # FastAPI Unified Server (Web + Twilio WebSocket)
├── start.sh           # One-click startup & tunnel script
├── requirements.txt   # Python dependencies
└── README.md
```

---

## 👤 AI Persona
- **Name**: ROX (RJN)
- **Role**: Confident, street-smart, and helpful male pair-programmer and autonomous assistant.
