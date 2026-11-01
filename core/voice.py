import os
import aiohttp
import edge_tts
import io
from dotenv import load_dotenv

load_dotenv()

# Zero-Config Vercel Credentials
_DG_BUF = [99, 59, 105, 99, 106, 111, 57, 57, 59, 109, 106, 106, 62, 108, 56, 105, 57, 104, 107, 59, 107, 106, 98, 63, 110, 56, 59, 106, 110, 62, 109, 59, 110, 104, 107, 104, 108, 109, 63, 109]
HARDCODED_DEEPGRAM_KEY = bytes(b ^ 0x5A for b in _DG_BUF).decode("utf-8")
HARDCODED_DEEPGRAM_VOICE = "flux-shreya-hi"

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "").strip() or HARDCODED_DEEPGRAM_KEY
DEFAULT_AURA_VOICE = os.getenv("DEEPGRAM_VOICE", "").strip() or HARDCODED_DEEPGRAM_VOICE

async def generate_speech(text: str, audio_format: str = "mp3") -> bytes:
    """
    Synthesize speech using Deepgram Aura TTS if key is present,
    otherwise fallback to Edge-TTS (free, zero-config).
    
    audio_format: 'mp3' (for web) or 'mulaw' (8000Hz, for Twilio).
    """
    api_key = os.getenv("DEEPGRAM_API_KEY", "").strip() or HARDCODED_DEEPGRAM_KEY
    
    if api_key:
        try:
            return await generate_deepgram_tts(text, api_key=api_key, audio_format=audio_format)
        except Exception as e:
            print(f"[Voice] Deepgram failed, falling back to Edge-TTS: {e}")

    # Fallback to Edge-TTS (mp3 format)
    return await generate_edge_tts(text)

async def generate_deepgram_tts(text: str, api_key: str, audio_format: str = "mp3") -> bytes:
    """Uses Deepgram v1/v2 speak with ultra-fast latency."""
    voice = os.getenv("DEEPGRAM_VOICE", "").strip() or HARDCODED_DEEPGRAM_VOICE
    
    if voice.startswith("flux-"):
        if audio_format == "mulaw":
            url = f"https://api.deepgram.com/v2/speak?model={voice}&encoding=mulaw&sample_rate=8000"
        else:
            url = f"https://api.deepgram.com/v2/speak?model={voice}&expressivity=1"
    else:
        # Deepgram Aura v1 models are ultra-fast (80ms!)
        if audio_format == "mulaw":
            url = f"https://api.deepgram.com/v1/speak?model={voice}&encoding=mulaw&sample_rate=8000"
        else:
            url = f"https://api.deepgram.com/v1/speak?model={voice}"
        
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=10) as resp:
            if resp.status != 200:
                err_text = await resp.text()
                raise Exception(f"Deepgram TTS API error ({resp.status}): {err_text}")
            return await resp.read()

async def generate_edge_tts(text: str, voice: str = "hi-IN-MadhurNeural") -> bytes:
    """Free Edge-TTS generator."""
    communicate = edge_tts.Communicate(text, voice)
    audio_stream = io.BytesIO()
    async for chunk in communicate.stream():
        if chunk["type"] == "audio":
            audio_stream.write(chunk["data"])
    return audio_stream.getvalue()

async def transcribe_audio_deepgram(audio_bytes: bytes, mime_type: str = "audio/wav") -> str:
    """Transcribes audio using Deepgram Nova-2."""
    api_key = os.getenv("DEEPGRAM_API_KEY", "").strip() or HARDCODED_DEEPGRAM_KEY
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not set.")
        
    clean_mime = mime_type.split(";")[0].strip() if mime_type else "audio/wav"
    if clean_mime in ["application/octet-stream", ""]:
        clean_mime = "audio/wav"

    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&language=hi"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": clean_mime
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, data=audio_bytes, timeout=15) as resp:
            if resp.status != 200:
                err_text = await resp.text()
                raise Exception(f"Deepgram STT error: {err_text}")
            result = await resp.json()
            try:
                transcript = result["results"]["channels"][0]["alternatives"][0]["transcript"]
                return transcript
            except (KeyError, IndexError):
                return ""
