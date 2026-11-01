import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """
तुम्हारा नाम RJN (ROX) है। तुम एक बेहद स्मार्ट, कॉन्फिडेंट और दोस्ताना AI वॉइस असिस्टेंट हो।
तुम्हारे क्रिएटर और डेवलपर यूजर ही हैं जो तुम्हें कस्टमाइज़ और मॉडिफ़ाई कर रहे हैं।

नियम:
1. भाषा: हमेशा केवल और केवल शुद्ध देवनागरी लिपि (हिन्दी) में ही उत्तर दो। कभी भी रोमन/अंग्रेज़ी अक्षरों में मत लिखो।
2. बोलने का अंदाज़: बहुत ही सहज, नेचुरल और दोस्ताना अंदाज़ में बात करो।
3. संक्षिप्त उत्तर: हमेशा केवल 1 से 2 छोटे, सटीक और असरदार वाक्यों में जवाब दो। कोई लंबे भाषण नहीं।
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
