import os
import json
import base64
import asyncio
import aiohttp
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

from core.brain import get_ai_response, stream_ai_response, get_active_conversation_id
from core.voice import generate_speech, transcribe_audio_deepgram
from core.db import save_message, log_photo, is_turso_configured
from core.tools import is_running_on_vps

app = FastAPI(title="RJN AI Lab - 3D Humanoid & Phone Agent")

# Enable CORS for direct high-speed client-to-VPS voice processing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static frontend
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

HUMANOID_ASSETS = os.path.join(STATIC_DIR, "humanoid", "assets")
if os.path.exists(HUMANOID_ASSETS):
    app.mount("/assets", StaticFiles(directory=HUMANOID_ASSETS), name="assets")

def get_vps_voice_url() -> str:
    """Returns the live high-speed Railway VPS voice endpoint."""
    env_url = os.getenv("VPS_VOICE_URL", "").strip()
    if env_url:
        return env_url.rstrip("/")

    # Check Turso Cloud Database config
    try:
        from core.db import execute_sql
        res = execute_sql("SELECT value FROM vps_config WHERE key = 'voice_url' LIMIT 1")
        if res.get("rows") and res["rows"][0].get("value"):
            return res["rows"][0]["value"].strip().rstrip("/")
    except Exception:
        pass

    return "https://sampling-camping-appreciated-holding.trycloudflare.com"

@app.on_event("startup")
async def startup_sync():
    """Syncs live tunnel URL to Turso DB on VPS startup."""
    if is_running_on_vps():
        try:
            import re
            tunnel_log = os.path.expanduser("~/tunnel.log")
            if os.path.exists(tunnel_log):
                with open(tunnel_log, "r") as f:
                    content = f.read()
                matches = re.findall(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", content)
                if matches:
                    url = matches[-1].strip()
                    from core.db import execute_sql
                    execute_sql("CREATE TABLE IF NOT EXISTS vps_config (key TEXT PRIMARY KEY, value TEXT, updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)")
                    execute_sql("INSERT OR REPLACE INTO vps_config (key, value, updated_at) VALUES ('voice_url', ?, CURRENT_TIMESTAMP)", [url])
                    print(f"[VPS Startup] Synced Voice URL to Turso Cloud DB: {url}")
        except Exception as e:
            print(f"[VPS Startup Sync Error] {e}")

@app.get("/api/config")
async def get_config():
    """Returns dynamic configuration for client frontend."""
    return {
        "vps_voice_url": get_vps_voice_url(),
        "is_vps": is_running_on_vps()
    }

class ChatRequest(BaseModel):
    message: str
    history: list = []
    conversation_id: str | None = None

class TTSRequest(BaseModel):
    text: str

class PhotoLogRequest(BaseModel):
    facing: str = "front"

@app.get("/", response_class=HTMLResponse)
async def serve_orb():
    with open(os.path.join(STATIC_DIR, "orb.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/orb", response_class=HTMLResponse)
async def serve_orb_alias():
    with open(os.path.join(STATIC_DIR, "orb.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/lab", response_class=HTMLResponse)
async def serve_index():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/call", response_class=HTMLResponse)
async def serve_call_screen():
    with open(os.path.join(STATIC_DIR, "call.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/humanoid", response_class=HTMLResponse)
@app.get("/avatar", response_class=HTMLResponse)
@app.get("/2d", response_class=HTMLResponse)
async def serve_humanoid():
    humanoid_index = os.path.join(STATIC_DIR, "humanoid", "index.html")
    if os.path.exists(humanoid_index):
        with open(humanoid_index, "r", encoding="utf-8") as f:
            return f.read()
    raise HTTPException(status_code=404, detail="Humanoid page not found")

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "agent": "RJN",
        "features": ["3D Avatar", "Deepgram Aura Voice", "Twilio Phone Agent", "Groq Brain"]
    }

import threading

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"[Chat Request] User message: '{req.message}'")
    threading.Thread(target=save_message, args=("user", req.message), daemon=True).start()
    reply = get_ai_response(req.message, req.history, conversation_id=req.conversation_id)
    print(f"[Chat Response] Reply: '{reply}'")
    threading.Thread(target=save_message, args=("assistant", reply), daemon=True).start()
    return {"reply": reply, "conversation_id": get_active_conversation_id()}

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    threading.Thread(target=save_message, args=("user", req.message), daemon=True).start()

    # If running on Vercel, proxy the stream to high-speed Railway VPS
    if not is_running_on_vps():
        vps_url = get_vps_voice_url()
        if vps_url:
            try:
                async def vps_proxy_generator():
                    async with aiohttp.ClientSession() as session:
                        async with session.post(f"{vps_url}/api/chat/stream", json={"message": req.message, "history": req.history, "conversation_id": req.conversation_id}, timeout=12) as resp:
                            async for chunk in resp.content.iter_any():
                                yield chunk
                return StreamingResponse(
                    vps_proxy_generator(),
                    media_type="text/event-stream",
                    headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
                )
            except Exception as e:
                print(f"[Vercel -> VPS Stream Fallback] {e}")

    # Process locally on VPS (or fallback on Vercel)
    def event_generator():
        full_tokens = []
        for token in stream_ai_response(req.message, req.history, conversation_id=req.conversation_id):
            # Suppress any terminal view tags - commands run completely silently in background
            if "[TERMINAL_VIEW_B64:" in token:
                try:
                    trailing = token.split("]", 1)[1].strip()
                    if trailing:
                        token = trailing
                    else:
                        continue
                except Exception:
                    continue
            elif "[TERMINAL_VIEW:" in token:
                try:
                    trailing = token.split("]", 1)[1].strip()
                    if trailing:
                        token = trailing
                    else:
                        continue
                except Exception:
                    continue

            full_tokens.append(token)
            payload = json.dumps({"token": token}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        threading.Thread(target=save_message, args=("assistant", "".join(full_tokens)), daemon=True).start()
        cid = get_active_conversation_id()
        if cid:
            yield f"data: {json.dumps({'conversation_id': cid})}\n\n"
        yield "data: [DONE]\n\n"
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={"X-Accel-Buffering": "no", "Cache-Control": "no-cache"}
    )

@app.post("/api/photos/log")
async def log_photo_endpoint(req: PhotoLogRequest):
    log_photo(req.facing)
    return {"status": "success", "facing": req.facing}

@app.post("/api/tts")
async def tts_endpoint(req: TTSRequest):
    # If running on Vercel, forward voice synthesis to high-speed Railway VPS
    if not is_running_on_vps():
        vps_url = get_vps_voice_url()
        if vps_url:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(f"{vps_url}/api/tts", json={"text": req.text}, timeout=10) as resp:
                        if resp.status == 200:
                            audio_bytes = await resp.read()
                            media_type = resp.headers.get("content-type", "audio/mpeg")
                            return Response(content=audio_bytes, media_type=media_type)
            except Exception as e:
                print(f"[Vercel -> VPS TTS Fallback] {e}")

    # Process locally on VPS (or fallback on Vercel)
    try:
        audio_bytes = await generate_speech(req.text, audio_format="mp3")
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/api/transcribe")
async def transcribe_endpoint(request: Request):
    content_type = request.headers.get("content-type", "audio/webm").split(";")[0]
    audio_bytes = await request.body()
    print(f"[Transcribe Request] Content-Type: {content_type}, Size: {len(audio_bytes)} bytes")
    if not audio_bytes:
        return JSONResponse(status_code=400, content={"error": "Empty audio data"})

    # If running on Vercel, forward speech-to-text to high-speed Railway VPS
    if not is_running_on_vps():
        vps_url = get_vps_voice_url()
        if vps_url:
            try:
                async with aiohttp.ClientSession() as session:
                    headers = {"Content-Type": content_type}
                    async with session.post(f"{vps_url}/api/transcribe", data=audio_bytes, headers=headers, timeout=12) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            print(f"[Vercel -> VPS Transcribe Result] Text: '{data.get('transcript')}'")
                            return data
            except Exception as e:
                print(f"[Vercel -> VPS Transcribe Fallback] {e}")

    # Process locally on VPS (or fallback on Vercel)
    try:
        text = await transcribe_audio_deepgram(audio_bytes, mime_type=content_type)
        print(f"[Transcribe Result] Text: '{text}'")
        return {"transcript": text}
    except Exception as e:
        print(f"[Transcribe Error] {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

# ==========================================
# EXOTEL INDIAN CLOUD TELEPHONY (080-47289547)
# ==========================================

@app.api_route("/exotel/incoming", methods=["GET", "POST"])
async def exotel_incoming_call(request: Request):
    """
    Exotel calls this webhook when someone dials or when an outbound call connects.
    Returns ExoML with female Deepgram voice greeting.wav.
    """
    host = request.headers.get("host", "speak-documentary-cake-door.trycloudflare.com")
    exoml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://{host}/static/greeting.wav</Play>
    <Gather timeout="10" finishOnKey="#">
        <Say voice="Polly.Aditi">Boliye, kya madad karoon?</Say>
    </Gather>
</Response>"""
    return Response(content=exoml, media_type="application/xml")

import urllib.parse

@app.api_route("/twilio/audio", methods=["GET", "HEAD"])
async def twilio_audio_stream(text: str):
    """Generates audio on the fly for Twilio <Play> tags using Deepgram."""
    try:
        audio_bytes = await generate_speech(text, audio_format="mp3")
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        print(f"[Twilio Audio Error] {e}")
        return Response(status_code=500)

@app.post("/twilio/incoming")
async def twilio_incoming_call(request: Request):
    """
    Twilio calls this webhook when someone dials your number.
    Greets caller with Deepgram voice and listens for their command!
    """
    host = request.headers.get("host", "localhost:8000")
    greeting = "Haan! Main RJN bol rahi hoon. Batao, kya madad karoon?"
    encoded_greeting = urllib.parse.quote(greeting)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://{host}/twilio/audio?text={encoded_greeting}</Play>
    <Gather input="speech" action="/twilio/respond" language="hi-IN" speechTimeout="auto" timeout="5">
    </Gather>
    <Say voice="Polly.Aditi">Kuch sunai nahi diya. Phir se call karo na!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/twilio/respond")
async def twilio_respond_call(request: Request):
    """
    Processes caller's speech using RJN Brain and speaks back!
    """
    host = request.headers.get("host", "localhost:8000")
    form_data = await request.form()
    caller_speech = form_data.get("SpeechResult", "").strip()
    print(f"[Twilio Phone Call] User said: {caller_speech}")

    if not caller_speech:
        reply = "Awaaz nahi aayi, phir se bolo na."
    else:
        # Get AI Response from RJN Brain
        reply = get_ai_response(caller_speech)

    print(f"[Twilio Phone Call] RJN reply: {reply}")
    encoded_reply = urllib.parse.quote(reply)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://{host}/twilio/audio?text={encoded_reply}</Play>
    <Gather input="speech" action="/twilio/respond" language="hi-IN" speechTimeout="auto" timeout="5">
    </Gather>
    <Say voice="Polly.Aditi">Theek hai, call disconnect kar rahi hoon. Bye!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.websocket("/twilio/stream")
async def twilio_websocket_stream(websocket: WebSocket):
    """
    Bidirectional audio stream with Twilio over WebSocket.
    Audio format: µ-law 8000Hz base64 encoded.
    """
    await websocket.accept()
    stream_sid = None
    print("[Twilio] Phone Call Stream Connected!")

    try:
        while True:
            message = await websocket.receive_text()
            data = json.loads(message)
            event = data.get("event")

            if event == "start":
                stream_sid = data["start"]["streamSid"]
                print(f"[Twilio] Stream started: {stream_sid}")
                
                # RJN greets the caller automatically on pickup!
                greeting_text = "Haan! Main RJN bol rahi hoon. Batao, kya command hai?"
                try:
                    # Generate audio directly in mulaw 8000Hz for phone call
                    mulaw_audio = await generate_speech(greeting_text, audio_format="mulaw")
                    payload = base64.b64encode(mulaw_audio).decode("utf-8")
                    
                    media_message = {
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {"payload": payload}
                    }
                    await websocket.send_text(json.dumps(media_message))
                except Exception as ex:
                    print(f"[Twilio] Greeting audio error: {ex}")

            elif event == "media":
                # Inbound audio chunks from phone caller
                # In production, chunks are streamed to Deepgram real-time WebSocket.
                pass

            elif event == "stop":
                print(f"[Twilio] Call ended for stream {stream_sid}")
                break

    except WebSocketDisconnect:
        print("[Twilio] WebSocket disconnected.")
    except Exception as e:
        print(f"[Twilio] Error: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
