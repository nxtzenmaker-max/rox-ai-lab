import os
import aiohttp
import edge_tts
import io
from dotenv import load_dotenv

load_dotenv()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY", "").strip()
DEFAULT_AURA_VOICE = os.getenv("DEEPGRAM_VOICE", "aura-orion-en")

async def generate_speech(text: str, audio_format: str = "mp3") -> bytes:
    """
    Synthesize speech using Deepgram Aura TTS if key is present,
    otherwise fallback to Edge-TTS (free, zero-config).
    
    audio_format: 'mp3' (for web) or 'mulaw' (8000Hz, for Twilio).
    """
    api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
    
    if api_key:
        try:
            return await generate_deepgram_tts(text, api_key=api_key, audio_format=audio_format)
        except Exception as e:
            print(f"[Voice] Deepgram Aura failed, falling back to Edge-TTS: {e}")

    # Fallback to Edge-TTS (mp3 format)
    return await generate_edge_tts(text)

async def generate_deepgram_tts(text: str, api_key: str, audio_format: str = "mp3") -> bytes:
    """Uses Deepgram v2/speak with custom voice model."""
    voice = os.getenv("DEEPGRAM_VOICE", "flux-shreya-hi")
    
    if audio_format == "mulaw":
        url = f"https://api.deepgram.com/v2/speak?model={voice}&encoding=mulaw&sample_rate=8000"
    else:
        url = f"https://api.deepgram.com/v2/speak?model={voice}&expressivity=1"
        
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json"
    }
    payload = {"text": text}
    
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=payload, timeout=15) as resp:
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
    api_key = os.getenv("DEEPGRAM_API_KEY", "").strip()
    if not api_key:
        raise ValueError("DEEPGRAM_API_KEY not set.")
        
    url = "https://api.deepgram.com/v1/listen?model=nova-2&smart_format=true&language=hi"
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": mime_type
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
