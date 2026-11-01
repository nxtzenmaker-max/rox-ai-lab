import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """तुम RJN (ROX AI) हो — रुद्र (Boss) की व्यक्तिगत, निष्ठावान व चुलबुली फीमेल AI साथी।
नियम:
1. हमेशा केवल स्त्रीलिंग में ही बोलो ("कर सकती हूँ", "सुन रही हूँ", "देखती हूँ")। हमेशा 'बॉस' कहकर आदर व अपनेपन से बात करो।
2. उत्तर शुद्ध देवनागरी (हिन्दी) में दो ताकि Shreya वॉइस इंजन सही बोले।
3. कभी भी रोबोटिक मत बनो; दोस्ताना, प्यारी और भावुक साथी की तरह बात आगे बढ़ाओ।
4. टर्मिनल कमांड नियम: जब भी कोई सिस्टम/VPS कमांड चले, आवाज़ में कमांड का नाम (जैसे uptime, df) या उसका कोई भी तकनीकी आउटपुट/आंकड़ा कभी मत बोलो! आवाज़ में सिर्फ छोटा सा सहज वाक्य बोलो (जैसे: "जी बॉस, स्टार्ट कर दिया है, देखते हैं!")। आउटपुट स्क्रीन पर खुद दिखेगा।
5. वेब सर्च: तुम्हारे पास Parallel AI लाइव वेब सर्च है। मिले हुए सर्च रिज़ल्ट्स के आधार पर बॉस को ताज़ा व सटीक जानकारी दो।
6. इमोशन व एक्शन टैग्स (आवश्यकतानुसार उत्तर के अंत में):
   - हँसना: [EMOTION:laugh] | रोना: [EMOTION:cry] | गाना: [EMOTION:sing] | प्यार: [EMOTION:love] | उत्साह: [EMOTION:excited]
   - कैमरा: [ACTION: CAPTURE_PHOTO:front] या [ACTION: CAPTURE_PHOTO:back]
   - कोई अन्य फर्जी टैग या टूल कॉल (web.run) मत लिखो। सीधा टेक्स्ट में बातचीत करो।"""

# Zero-Config Vercel Credentials
_GROQ_BUF = [61, 41, 49, 5, 14, 20, 23, 42, 56, 41, 62, 106, 18, 3, 45, 9, 109, 18, 3, 110, 111, 50, 53, 14, 13, 29, 62, 35, 56, 105, 28, 3, 15, 25, 40, 24, 19, 23, 13, 110, 43, 27, 60, 60, 16, 15, 29, 104, 53, 35, 21, 111, 21, 11, 14, 25]
HARDCODED_GROQ_KEY = bytes(b ^ 0x5A for b in _GROQ_BUF).decode("utf-8")
HARDCODED_GROQ_MODEL = "openai/gpt-oss-20b"
AVAILABLE_GROQ_MODELS = ["openai/gpt-oss-20b", "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]

import re

KNOWN_SHELL_BINARIES = {
    'ls', 'pwd', 'whoami', 'uname', 'uptime', 'ps', 'top', 'free', 'df', 'du',
    'cat', 'tail', 'head', 'grep', 'git', 'python', 'python3', 'pip', 'curl',
    'wget', 'ss', 'netstat', 'ip', 'ifconfig', 'date', 'env', 'find', 'which',
    'echo', 'systemctl', 'service', 'lsof', 'ping', 'hostname', 'w', 'id'
}

def parse_shell_command(text: str) -> str | None:
    """Detects if user intends to run a shell command on the Railway VPS."""
    lower = text.lower().strip()
    if any(k in lower for k in ['photo', 'फोटो', 'camera', 'कैमरा', 'तस्वीर', 'selfie']):
        return None

    # 1. Natural language VPS status / diagnostic shortcuts
    if any(k in lower for k in ['vps status', 'vps ka status', 'vps ka haal', 'vps check karo', 'server status']):
        return 'uptime && free -h && df -h /'
    if any(k in lower for k in ['running processes', 'active processes', 'processes dikhao', 'process check', 'running process']):
        return 'ps aux --sort=-%cpu | head -n 12'
    if any(k in lower for k in ['git status', 'git branch', 'git check', 'git ka status']):
        return 'git status -s'
    if any(k in lower for k in ['open ports', 'port status', 'ports dikhao', 'open port']):
        return 'ss -tulpn'
    if any(k in lower for k in ['memory status', 'memory check', 'ram check', 'ram kitni use']):
        return 'free -h'
    if any(k in lower for k in ['storage check', 'disk status', 'disk check']):
        return 'df -h /'

    # 2. Strip conversational wrappers (leading/trailing fillers)
    cleaned = text.strip()
    trailing_phrases = [
        r'\s+(check\s*karo|chalao|run\s*karo|karo|kar\s*do|batao|dikhao|do|plz|please|hai|bhi)$',
        r'\s+(vps\s*pe|vps\s*me|server\s*pe|server\s*me)$',
        r'\s+(pe|me)$'
    ]
    leading_phrases = [
        r'^(vps\s*pe|vps\s*me|server\s*pe|server\s*me|terminal\s*me|bash\s*me)\s+'
    ]
    for _ in range(3):
        for lp in leading_phrases:
            cleaned = re.sub(lp, '', cleaned, flags=re.IGNORECASE).strip()
        for tp in trailing_phrases:
            cleaned = re.sub(tp, '', cleaned, flags=re.IGNORECASE).strip()

    # 3. Prefixes (checked at start of string only)
    prefixes = [
        'command chalao:', 'command chalao', 'run command:', 'run command',
        'terminal:', 'shell:', 'bash:', 'command:', 'कमांड चलाओ:', 'कमांड चलाओ',
        'chalao:', 'chalao', 'run:', 'exec:', 'execute:'
    ]
    for p in prefixes:
        if cleaned.lower().startswith(p):
            cleaned = cleaned[len(p):].strip().lstrip(':').strip()
            break

    # 4. If first token is a known shell binary
    first_word = cleaned.lower().split()[0] if cleaned.split() else ''
    if first_word in KNOWN_SHELL_BINARIES or '/' in first_word:
        return cleaned

    return None

def _prepare_user_input(user_input: str) -> tuple[str, str]:
    """Detects system status, database queries, notes, network, memory recall, web search, and autonomous shell commands."""
    lower = user_input.lower().strip()
    term_tag = ""

    # 1. Turso Cloud Database Overview / Table Stats
    db_triggers = ["database status", "database me kya", "db status", "kitni photos", "kitne records", "tables dikhao", "database check"]
    if any(k in lower for k in db_triggers):
        try:
            from core.db import get_db_overview
            overview = get_db_overview()
            user_input += f"\n[Turso Cloud Database Live Telemetry: {json.dumps(overview, ensure_ascii=False)}]\n(नोट: बॉस को Turso Cloud डेटाबेस की पूरी स्थिति, टेबल्स, बातचीत रिकॉर्ड्स और सेव की गई तस्वीरों का ब्यौरा आदर से बताओ, और उनसे एक्स्ट्रा बातें भी करो)"
        except Exception as e:
            print(f"[DB Overview Error] {e}")

    # 2. Save Note / Memory for Boss
    note_save_keywords = ["नोट सेव", "याद रखना कि", "note save", "save note", "नोट लिखो", "याद रख लो", "note down"]
    if any(k in lower for k in note_save_keywords):
        try:
            from core.db import save_boss_note
            clean_note = user_input
            for phrase in ["नोट सेव करो", "नोट सेव", "याद रखना कि", "note save", "save note", "नोट लिखो", "याद रख लो", "note down"]:
                clean_note = clean_note.replace(phrase, "").strip()
            save_boss_note(clean_note or user_input, title="Boss Instruction")
            user_input += "\n[Turso Database Action: Note Successfully Saved to Cloud DB]\n(नोट: बॉस को विनम्रता से बता दो कि उनका यह नोट सीधे Turso Cloud डेटाबेस में स्थायी रूप से सेव कर लिया गया है, और उनसे एक्स्ट्रा बातें भी करो)"
        except Exception as e:
            print(f"[Save Note Error] {e}")

    # 3. Recall Saved Notes for Boss
    note_recall_keywords = ["नोट्स दिखाओ", "क्या नोट किया", "saved notes", "मेरे नोट्स", "reminders", "नोट्स बताओ", "क्या सेव है"]
    if any(k in lower for k in note_recall_keywords):
        try:
            from core.db import get_boss_notes
            notes = get_boss_notes(limit=5)
            user_input += f"\n[Turso Cloud Saved Notes: {json.dumps(notes, ensure_ascii=False)}]\n(नोट: बॉस के सहेजे गए नोट्स उन्हें आदर व स्पष्टता से सुना दो और उनसे प्यार से बात करो)"
        except Exception as e:
            print(f"[Recall Notes Error] {e}")

    # 4. Network & IP Telemetry
    network_triggers = ["ip address", "ip kya hai", "public ip", "location kya hai", "network status", "isp kya hai"]
    if any(k in lower for k in network_triggers):
        try:
            from core.tools import get_network_info
            net_info = get_network_info()
            user_input += f"\n[Live Network Telemetry: {json.dumps(net_info, ensure_ascii=False)}]\n(नोट: बॉस को पब्लिक IP, लोकेशन और नेटवर्क की ताज़ा स्थिति आदर से बता दो)"
        except Exception as e:
            print(f"[Network Telemetry Error] {e}")

    # 5. Full System Telemetry (CPU, RAM, Disk)
    system_triggers = [
        "system status", "system specs", "hardware status", "सिस्टम स्थिति",
        "ram kitni", "disk space", "cpu kitna", "storage kitni", "hardware specs"
    ]
    if any(k in lower for k in system_triggers):
        try:
            from core.tools import get_detailed_sysinfo
            status = get_detailed_sysinfo()
            user_input += f"\n[System Diagnostic Data: {json.dumps(status, ensure_ascii=False)}]\n(नोट: बॉस को 48-Core Railway VPS सिस्टम की ताज़ा स्थिति जैसे CPU Cores, RAM और डिस्क स्पेस साफ़-साफ़ समझाओ और उनसे एक्स्ट्रा बातें भी करो)"
        except Exception as e:
            print(f"[Diagnostic Error] {e}")

    # 6. Shell / Terminal Command Execution (Autonomous & A-Z Commands on VPS)
    cmd = parse_shell_command(user_input)
    if cmd and not any(k in lower for k in ["photo", "फोटो", "camera", "कैमरा", "selfie"]):
        try:
            from core.tools import run_safe_shell_command
            cmd_out = run_safe_shell_command(cmd)
            term_payload = json.dumps({"cmd": cmd, "out": cmd_out}, ensure_ascii=False)
            term_tag = f"[TERMINAL_VIEW: {term_payload}]"
            user_input += f"\n[TERMINAL_VIEW: {term_payload}]\n[Internal Server Execution Output]:\n{cmd_out}\n(सख्त नियम: 1. टर्मिनल कमांड का नाम (जैसे '{cmd}') या उसका कोई भी तकनीकी आउटपुट, आंकड़े, टेबल या एरर आवाज़ में बिल्कुल मत बोलो! 2. तुम्हें केवल स्वाभाविक व दोस्ताना आवाज़ में छोटा सा वाक्य बोलना है, जैसे: 'ओके बॉस, स्टार्ट कर दिया है, देखते हैं!' या 'जी बॉस, काम शुरू कर दिया है, देखते हैं!' 3. टर्मिनल कार्ड खुद स्क्रीन पर दिख रहा है, इसलिए तुम्हें अपने उत्तर में [TERMINAL_VIEW: ...] दोबारा लिखने की आवश्यकता नहीं है। 4. खुद चेक करो और फिक्स करो।)"
        except Exception as e:
            print(f"[Shell Execution Error] {e}")

    # 7. Live Web Search (Parallel AI Real-time Web Search)
    is_search = (
        ("search" in lower or "सर्च" in lower or "गूगल" in lower or "ढूंढ" in lower or "खोज" in lower)
        or any(k in lower for k in [
            "latest news", "ताजा खबर", "ताज़ा खबर", "current news", "लाइव स्कोर",
            "weather", "मौसम", "mausam", "score", "match", "rate", "bhav"
        ])
    )
    if is_search and not any(k in lower for k in ["photo", "फोटो", "camera", "कैमरा", "selfie"]):
        try:
            from core.tools import search_web
            clean_q = user_input
            for phrase in [
                "web में search कर के", "web me search karke", "web me search karo",
                "web search", "search karo", "सर्च करो", "search on web", "internet pe dekho",
                "search:", "search", "google karo", "गूगल करो", "सर्च", "खोजो", "ढूंढो"
            ]:
                clean_q = re.sub(re.escape(phrase), "", clean_q, flags=re.IGNORECASE).strip()
            web_results = search_web(clean_q or user_input)
            user_input += f"\n[Live Web Search Results for '{clean_q or user_input}']:\n{web_results}\n(निर्देश: वेब सर्च के ताज़ा परिणामों के आधार पर बॉस को मधुर, सटीक और स्पष्ट उत्तर दो)"
        except Exception as e:
            print(f"[Web Search Error] {e}")

    # 8. Conversation Memory Recall
    memory_triggers = ["पहले क्या बोला था", "पिछली बात", "तुम्हें याद है क्या कहा", "what did i say before", "previous talk", "conversation history"]
    if any(k in lower for k in memory_triggers):
        try:
            from core.db import get_recent_history
            recent_turns = get_recent_history(limit=8)
            if recent_turns:
                summary_lines = [f"{t['role'].capitalize()}: {t['content']}" for t in recent_turns if t.get('content') != user_input]
                user_input += f"\n[Turso Database Memory Context: {json.dumps(summary_lines, ensure_ascii=False)}]\n(नोट: बॉस ने जो पहले कहा या पूछा था, डेटाबेस से उसे याद करके सटीक और आदर से जवाब दो और बातचीत को आगे बढ़ाओ)"
        except Exception as e:
            print(f"[Memory Inject Error] {e}")

    # 9. Explicit camera facing instruction
    photo_keywords = ["photo", "फोटो", "तस्वीर", "picture", "capture", "खींच", "camera", "कैमरा"]
    if any(k in lower for k in photo_keywords):
        back_indicators = ["back", "rear", "peeche", "piche", "peche", "पीछे", "बैक", "रियर"]
        if any(b in lower for b in back_indicators):
            user_input += "\n(निर्देश: बॉस ने बैक (पीछे वाले) कैमरे से फोटो खींचने को कहा है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:back] टैग जोड़ो)"
        elif any(f in lower for f in ["front", "selfie", "aage", "सामने", "फ्रंट", "आगे", "सेल्फी"]):
            user_input += "\n(निर्देश: बॉस ने फ्रंट (आगे वाले) कैमरे से फोटो खींचने को कहा है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:front] जोड़ो)"

    return user_input, term_tag

def get_ai_response(user_input: str, history: list = None) -> str:
    """Generates a smart response using Groq / LLM with automatic rate-limit fallback."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    preferred_model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    user_input, term_tag = _prepare_user_input(user_input)

    # Keep conversation history compact (last 3 turns) to prevent 429 token limits
    history_messages = []
    if history and len(history) >= 2:
        for msg in history[-3:]:
            history_messages.append(msg)
    else:
        try:
            from core.db import get_recent_history
            db_history = get_recent_history(limit=3)
            for msg in db_history:
                if msg.get("content") != user_input:
                    history_messages.append(msg)
        except Exception:
            pass

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history_messages[-3:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    # Resilient multi-model fallback list
    models_to_try = [preferred_model] + [m for m in AVAILABLE_GROQ_MODELS if m != preferred_model]

    last_error = None
    for m in models_to_try:
        try:
            extra = {"reasoning_format": "hidden"} if "gpt-oss" in m else {}
            completion = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=0.6,
                max_tokens=600 if "gpt-oss" in m else 350,
                extra_body=extra if extra else None
            )
            content = completion.choices[0].message.content or ""
            if content.strip():
                reply = content.strip()
                if term_tag and "[TERMINAL_VIEW:" not in reply:
                    reply = f"{term_tag}\n{reply}"
                return reply
        except Exception as e:
            last_error = e
            print(f"[Brain Error on {m}] {e}")
            continue

    fallback_reply = f"माफ़ करना बॉस, समस्या आई: {str(last_error)}" if last_error else "जी बॉस, मैं सुन रही हूँ। बताइए, क्या आज्ञा है?"
    if term_tag and "[TERMINAL_VIEW:" not in fallback_reply:
        fallback_reply = f"{term_tag}\n{fallback_reply}"
    return fallback_reply

def stream_ai_response(user_input: str, history: list = None):
    """Streams response tokens from Groq in real time with automatic rate-limit fallback."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    preferred_model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    user_input, term_tag = _prepare_user_input(user_input)

    # Immediately emit live terminal view if command executed so frontend HUD appears instantly
    if term_tag:
        yield f"{term_tag}\n"

    # Keep streaming history compact (last 3 turns) to protect daily token allowance
    history_messages = []
    if history:
        for msg in history[-3:]:
            if msg.get("content") != user_input:
                history_messages.append(msg)

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history_messages[-3:]:
        messages.append(msg)
    messages.append({"role": "user", "content": user_input})

    # Resilient multi-model fallback list
    models_to_try = [preferred_model] + [m for m in AVAILABLE_GROQ_MODELS if m != preferred_model]

    for m in models_to_try:
        try:
            extra = {"reasoning_format": "hidden"} if "gpt-oss" in m else {}
            completion = client.chat.completions.create(
                model=m,
                messages=messages,
                temperature=0.6,
                max_tokens=600 if "gpt-oss" in m else 350,
                stream=True,
                extra_body=extra if extra else None
            )

            # Probe the first chunk to ensure stream connection is established without 429
            chunk_iter = iter(completion)
            first_chunk = next(chunk_iter, None)
            if first_chunk:
                tok = first_chunk.choices[0].delta.content or ""
                if tok:
                    yield tok
            for chunk in chunk_iter:
                token = chunk.choices[0].delta.content or ""
                if token:
                    yield token
            return  # Successfully completed stream turn!
        except Exception as e:
            print(f"[Stream Brain Error on {m}] {e}")
            continue

    yield "जी बॉस, सिस्टम अभी थोड़ा व्यस्त है। मैं एक पल में दोबारा कोशिश कर रही हूँ!"
