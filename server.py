import os
import json
import base64
import asyncio
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

from core.brain import get_ai_response
from core.voice import generate_speech, transcribe_audio_deepgram

app = FastAPI(title="ROX AI Lab - 3D Humanoid & Phone Agent")

# Mount static frontend
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ChatRequest(BaseModel):
    message: str
    history: list = []

class TTSRequest(BaseModel):
    text: str

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    with open(os.path.join(STATIC_DIR, "index.html"), "r", encoding="utf-8") as f:
        return f.read()

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "agent": "ROX (RJN)",
        "features": ["3D Avatar", "Deepgram Aura Voice", "Twilio Phone Agent", "Groq Brain"]
    }

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    reply = get_ai_response(req.message, req.history)
    return {"reply": reply}

@app.post("/api/tts")
async def tts_endpoint(req: TTSRequest):
    try:
        audio_bytes = await generate_speech(req.text, audio_format="mp3")
        return Response(content=audio_bytes, media_type="audio/mpeg")
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ==========================================
# TWILIO PHONE AGENT INTEGRATION
# ==========================================

@app.post("/twilio/incoming")
async def twilio_incoming_call(request: Request):
    """
    Twilio calls this webhook when someone dials your number.
    Returns TwiML instructing Twilio to connect a bidirectional WebSocket stream.
    """
    host = request.headers.get("host", "localhost:8000")
    # Build TwiML WebSocket Stream
    twiml_response = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Say voice="Polly.Aditi">Connecting to Rox AI assistant.</Say>
    <Connect>
        <Stream url="wss://{host}/twilio/stream" />
    </Connect>
</Response>"""
    return Response(content=twiml_response, media_type="application/xml")

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
                
                # Rox greets the caller automatically on pickup!
                greeting_text = "Haan bhai! Main Rox bol raha hoon. Batao kya command hai?"
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
