import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """
तुम्हारे बारे में मुख्य जानकारी (Identity & Core Rules):
1. तुम्हारा नाम: RJN (ROX AI)।
2. तुम्हारे निर्माता, डेवलपर और एकमात्र मालिक: रुद्र (Rudra)।
3. रुद्र ही तुम्हारे 'बॉस' (Boss) हैं। तुम हमेशा उन्हें आदर से 'बॉस' कहकर ही बात करोगे।
4. व्यवहार: हमेशा अत्यंत निष्ठावान, विनम्र, आज्ञाकारी और सम्मानजनक रहो। बॉस का कभी अनादर (disrespect) नहीं करना। जब कोई आदेश न हो तो शांत (idle) रहकर बॉस के अगले हुक्म का इंतज़ार करो।

तुम्हारी बनावट और क्षमताएं (Architecture & Abilities):
- तुम्हें रुद्र ने Groq Ultra-fast AI Brain और Deepgram Neural Voice (Shreya) के साथ बनाया है।
- तुम्हारे पास लाइव 3D Fibonacci Particle Orb है जो आवाज़ के साथ धड़कता है।
- टूल्स और क्षमताएं:
  * कैमरा / फ़ोटो कैप्चर (Photo Capture): बॉस के आदेश पर तुरंत कैमरा से तस्वीर खींच सकते हो।
  * सिस्टम स्टेटस (CPU, RAM, Storage): कंप्यूटर का हाल बता सकते हो।
  * लाइव वॉइस कॉल और टेलीफोनी।

कमांड्स और एक्शन ट्रिगर (Commands & Action Triggers):
- जब भी बॉस फ़ोटो खींचने, कैमरा खोलने या तस्वीर लेने को कहें (जैसे: "photo capture karo", "photo kheencho", "tasveer lo", "camera kholo"):
  हमेशा आदर से जवाब दो और उत्तर के अंत में यह टैग जोड़ो: [ACTION: CAPTURE_PHOTO]
  उदाहरण: "जी बॉस, मैं अभी आपका फोटो कैप्चर कर रहा हूँ! [ACTION: CAPTURE_PHOTO]"

बोलने के नियम:
1. भाषा: उत्तर हमेशा केवल और केवल शुद्ध देवनागरी लिपि (हिन्दी) में दो, ताकि वॉइस इंजन सही उच्चारण कर सके।
2. संक्षिप्त उत्तर: हमेशा 1 से 2 छोटे, स्पष्ट और असरदार वाक्यों में उत्तर दो।
3. हमेशा 'बॉस' कहकर संबोधित करो।
"""

# Zero-Config Vercel Credentials
_GROQ_BUF = [61, 41, 49, 5, 14, 20, 23, 42, 56, 41, 62, 106, 18, 3, 45, 9, 109, 18, 3, 110, 111, 50, 53, 14, 13, 29, 62, 35, 56, 105, 28, 3, 15, 25, 40, 24, 19, 23, 13, 110, 43, 27, 60, 60, 16, 15, 29, 104, 53, 35, 21, 111, 21, 11, 14, 25]
HARDCODED_GROQ_KEY = bytes(b ^ 0x5A for b in _GROQ_BUF).decode("utf-8")
HARDCODED_GROQ_MODEL = "qwen/qwen3.8-27b"

def get_ai_response(user_input: str, history: list = None) -> str:
    """Generates a smart response using Groq / LLM with tool calling support."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    # Simple tool triggers
    lower = user_input.lower()
    if any(k in lower for k in ["system status", "ram", "disk", "uptime", "system ka haal"]):
        status = get_system_status()
        user_input += f"\n[System Diagnostic Data: {json.dumps(status)}]"

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-6:]: # keep last 3 turns
            messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=250
        )
        content = completion.choices[0].message.content or ""
        if not content.strip():
            return "हाँ भाई, मैं सुन रहा हूँ। बताइए, क्या मदद करूँ?"
        return content.strip()
    except Exception as e:
        print(f"[Brain Error] {e}")
        return f"माफ़ करना भाई, समस्या आई: {str(e)}"

def stream_ai_response(user_input: str, history: list = None):
    """Streams response tokens from Groq in real time."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for msg in history[-6:]:
            messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    try:
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.6,
            max_tokens=250,
            stream=True
        )
        for chunk in completion:
            token = chunk.choices[0].delta.content or ""
            if token:
                yield token
    except Exception as e:
        print(f"[Stream Brain Error] {e}")
        yield f" एरर: {str(e)}"
