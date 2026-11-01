import os
import json
import base64
import asyncio
from fastapi import FastAPI, Request, Response, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse, Response, StreamingResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment
load_dotenv()

from core.brain import get_ai_response, stream_ai_response
from core.voice import generate_speech, transcribe_audio_deepgram
from core.db import save_message, log_photo, is_turso_configured

app = FastAPI(title="ROX AI Lab - 3D Humanoid & Phone Agent")

# Mount static frontend
STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

class ChatRequest(BaseModel):
    message: str
    history: list = []

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

@app.get("/health")
async def health_check():
    return {
        "status": "online",
        "agent": "ROX (RJN)",
        "features": ["3D Avatar", "Deepgram Aura Voice", "Twilio Phone Agent", "Groq Brain"]
    }

import threading

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    print(f"[Chat Request] User message: '{req.message}'")
    threading.Thread(target=save_message, args=("user", req.message), daemon=True).start()
    reply = get_ai_response(req.message, req.history)
    print(f"[Chat Response] Reply: '{reply}'")
    threading.Thread(target=save_message, args=("assistant", reply), daemon=True).start()
    return {"reply": reply}

@app.post("/api/chat/stream")
async def chat_stream_endpoint(req: ChatRequest):
    threading.Thread(target=save_message, args=("user", req.message), daemon=True).start()
    def event_generator():
        full_tokens = []
        for token in stream_ai_response(req.message, req.history):
            full_tokens.append(token)
            payload = json.dumps({"token": token}, ensure_ascii=False)
            yield f"data: {payload}\n\n"
        threading.Thread(target=save_message, args=("assistant", "".join(full_tokens)), daemon=True).start()
        yield "data: [DONE]\n\n"
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/api/photos/log")
async def log_photo_endpoint(req: PhotoLogRequest):
    log_photo(req.facing)
    return {"status": "success", "facing": req.facing}

@app.post("/api/tts")
async def tts_endpoint(req: TTSRequest):
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
    greeting = "Haan bhai! Main Rox bol raha hoon. Batao kya hukam hai?"
    encoded_greeting = urllib.parse.quote(greeting)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://{host}/twilio/audio?text={encoded_greeting}</Play>
    <Gather input="speech" action="/twilio/respond" language="hi-IN" speechTimeout="auto" timeout="5">
    </Gather>
    <Say voice="Polly.Aditi">Bhai kuch sunai nahi diya. Phir se call karo!</Say>
</Response>"""
    return Response(content=twiml, media_type="application/xml")

@app.post("/twilio/respond")
async def twilio_respond_call(request: Request):
    """
    Processes caller's speech using Rox Brain and speaks back!
    """
    host = request.headers.get("host", "localhost:8000")
    form_data = await request.form()
    caller_speech = form_data.get("SpeechResult", "").strip()
    print(f"[Twilio Phone Call] User said: {caller_speech}")

    if not caller_speech:
        reply = "Bhai awaaz nahi aayi, phir se bolo."
    else:
        # Get AI Response from Rox Brain
        reply = get_ai_response(caller_speech)

    print(f"[Twilio Phone Call] Rox reply: {reply}")
    encoded_reply = urllib.parse.quote(reply)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Play>https://{host}/twilio/audio?text={encoded_reply}</Play>
    <Gather input="speech" action="/twilio/respond" language="hi-IN" speechTimeout="auto" timeout="5">
    </Gather>
    <Say voice="Polly.Aditi">Theek hai bhai, call disconnect kar raha hoon. Alvida!</Say>
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

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "8000"))
    uvicorn.run("server:app", host="0.0.0.0", port=port, reload=False)
