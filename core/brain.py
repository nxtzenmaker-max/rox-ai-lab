import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """
Tumhara naam ROX (RJN) hai. Tum ek ultra-smart, confident, aur stylish 3D AI assistant aur voice agent ho.
Tumhara communication style natural, friendly aur punchy Hinglish/Hindi me hai. 
Short, impactful aur actionable replies do. Live phone call ya 3D voice avatar me baat kar rahe ho isliye lamba lecture mat dena, conversational rehna.

Agar user kisi command ya system status ke baare me puche, to clear response dena.
"""

def get_ai_response(user_input: str, history: list = None) -> str:
    """Generates a smart response using Groq / LLM with tool calling support."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip()
    
    if not groq_api_key:
        return "Bhai, GROQ_API_KEY set nahi hai! .env file me key daal do."

    client = Groq(api_key=groq_api_key)
    model = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

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
            temperature=0.7,
            max_tokens=300
        )
        return completion.choices[0].message.content.strip()
    except Exception as e:
        return f"Arre bhai, LLM me issue aaya: {str(e)}"
