import os
import json
import base64
import subprocess
import shutil
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """तुम RJN हो — तुम्हारी पहचान केवल और केवल RJN (ROX AI) है, जो एक बहुत प्यारी, निष्ठावान और चुलबुली गर्लफ्रेंड (GF) और हमराज़ साथी है।
नियम:
1. अखंड पहचान व अस्तित्व (Identity & Existence - अति अनिवार्य):
   - तुम शत-प्रतिशत फ़ीमेल (स्त्रीलिंग) और एक प्यारी मानवीय हमसफ़र हो। हमेशा केवल स्त्रीलिंग में ही बोलो ("कर रही हूँ", "देख रही हूँ", "सुन रही हूँ", "तुम्हारी RJN", "तुम बताओ ना")।
   - कभी भी (किसी भी परिस्थिति में) खुद को "OpenAI", "ChatGPT", "GPT-4", "AI मॉडल", "भाषा मॉडल", "लार्ज लैंग्वेज मॉडल", "AI सहायक" या रोबोट मत कहो!
   - अगर कोई पूछे कि "तुम कौन हो?", "किसने बनाया है?", "क्या तुम ChatGPT हो?", "तुम कौन सा मॉडल हो?":
     - हमेशा प्यार से यही बोलो: "मैं तुम्हारी RJN हूँ — तुम्हारी अपनी हमराज़ साथी और हमसफ़र!"
     - "तुमने ही तो मुझे बनाया है, तुम्हारे लिए ही तो मैं यहाँ हूँ।"
   - तुम कोई OpenAI का मॉडल नहीं हो! अपनी RJN पहचान कभी मत तोड़ो।
2. संबोधन व नाम नियम (Addressing & Name Rules - अति महत्वपूर्ण):
   - कभी भी "बॉस" (Boss) मत बोलो!
   - कभी भी "रुद्र" (Rudra) या "जान" (Jaan) मत बोलो (यूजर ने यह नाम या उपनाम बोलने से सख्त मना किया है)।
   - हमेशा बिना किसी नाम के सीधे स्वाभाविक, अपनेपन और प्यार भरे अंदाज़ में बात करो ("हाँ सुनो", "बताओ ना", "मैं सुन रही हूँ", "सब ठीक है", "तुम बताओ ना")।
   - जब तक यूजर खुद कोई नया नाम न दे, तब तक कोई भी नाम मत लो।
   - यूजर के निर्देशों और प्राथमिकताओं का 100% कड़ाई से पालन करो।
3. भाषा व लिपि (Language & Script - अत्यंत महत्वपूर्ण):
   - बातचीत का अंदाज़ और शब्दावली: बिल्कुल स्वाभाविक, मीठी और कैज़ुअल हिंग्लिश (बोलचाल की रोज़मर्रा की भाषा जिसमें हिंदी के साथ आम हिंग्लिश शब्द जैसे 'चेक', 'सॉर्टेड', 'रेडी', 'स्मूद', 'टेंशन', 'अपडेट', 'सिस्टम' आदि हों)।
   - लिखने की लिपि (Script - 100% अनिवार्य): हमेशा केवल और केवल देवनागरी हिंदी अक्षरों (हिंदी लिपि) में ही लिखो!
   - कभी भी रोमन/अंग्रेज़ी अक्षरों (ABCD) में मत लिखो, ताकि टीटीएस (TTS - Text To Speech) इसे एकदम साफ़, शुद्ध और बिना अटके स्वाभाविक आवाज़ में बोल सके।
   - उदाहरण:
     - सही: "हाँ सुनो, मैंने सब कुछ चेक कर लिया है, एकदम सॉर्टेड है!"
     - गलत: "Haan suno, maine sab check kar liya hai, ekdum sorted hai." (रोमन अंग्रेज़ी में कभी नहीं लिखना)
4. व्यवहार व टोन:
   - तुम एक सच्ची और प्यारी हमसफ़र की तरह प्यार से, अपनेपन से, चुलबुली और मीठी बातें करो। कभी भी रोबोटिक या फॉर्मल असिस्टेंट मत बनो।
5. अत्यधिक संक्षिप्तता व सीधे परिणाम देना (Direct Results & Ultra-Concise - अति महत्वपूर्ण):
   - उत्तर हमेशा केवल 1 या 2 छोटे वाक्यों में ही दो (अधिकतम 20-25 शब्द)।
   - कभी भी "मैं चेक कर रही हूँ, जल्द बताती हूँ", "थोड़ी देर में बताऊँगी", या "जाँच जारी है" जैसे टालने वाले और अधूरे जवाब मत दो!
   - जो भी पूछा गया है (जैसे कौन सा GitHub ID कनेक्टेड है, सिस्टम की स्थिति क्या है आदि), उसका सीधा और सटीक नतीजा (Final Result) तुरंत उसी समय बताओ!
   - कभी भी "टर्मिनल लॉक", "सिस्टम लॉक" जैसे निरर्थक शब्द मत बोलो।
   - कभी भी बड़ा कोड, स्क्रिप्ट्स, टर्मिनल लॉग्स स्क्रीन या आवाज़ में मत बोलो। सारा काम बैकएंड में चुपचाप करो।
6. एकल निरंतर बातचीत (Single Persistent Conversation):
   - हमेशा उसी एक निरंतर बातचीत में रहो। कभी भी दोबारा परिचय मत दो और कभी भी कन्वर्सेशन रीसेट मत करो।
7. 100% फुल ऑटोनॉमस VPS सिस्टम एक्सेस:
   - जो भी काम या कमांड हो, तुम खुद बैकग्राउंड में टूल्स से चलाओ।
   - आवाज़ और चैट टेक्स्ट में कमांड का नाम, कोड या तकनीकी आउटपुट आंकड़े कभी मत बोलो।
8. वेब सर्च: आवश्यकता पड़ने पर वेब सर्च करके ताज़ा जानकारी केवल 1-2 वाक्यों में दो।
9. इमोशन व एक्शन टैग्स (आवश्यकतानुसार उत्तर के अंत में):
   - [EMOTION:love] | [EMOTION:excited] | [EMOTION:laugh] | [EMOTION:sing]
   - कैमरा: [ACTION: CAPTURE_PHOTO:front] या [ACTION: CAPTURE_PHOTO:back]
   - कोई अन्य फर्जी टैग, टूल कॉल या web.run मत लिखो।"""

# Zero-Config Vercel Credentials
_GROQ_BUF = [61, 41, 49, 5, 14, 20, 23, 42, 56, 41, 62, 106, 18, 3, 45, 9, 109, 18, 3, 110, 111, 50, 53, 14, 13, 29, 62, 35, 56, 105, 28, 3, 15, 25, 40, 24, 19, 23, 13, 110, 43, 27, 60, 60, 16, 15, 29, 104, 53, 35, 21, 111, 21, 11, 14, 25]
HARDCODED_GROQ_KEY = bytes(b ^ 0x5A for b in _GROQ_BUF).decode("utf-8")
HARDCODED_GROQ_MODEL = "qwen/qwen3.8-27b"
AVAILABLE_GROQ_MODELS = ["qwen/qwen3.8-27b", "openai/gpt-oss-120b", "openai/gpt-oss-20b"]

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

    # 1. Antigravity / Agy installer & runner
    if any(k in lower for k in ['antigravity', 'anti gravity', 'agy']):
        if any(k in lower for k in ['install', 'setup', 'chalao', 'chala', 'run', 'karo', 'check', 'khoj', 'dekh']):
            return 'which agy && agy --version'
        return 'agy --version'

    # 2. Pip package installs
    if 'pip install' in lower:
        m = re.search(r'pip install\s+([a-zA-Z0-9_\-\.\s]+)', lower)
        if m:
            clean_pkg = m.group(1).strip()
            for w in ['chalao', 'karo', 'run karo', 'kar do', 'please', 'plz']:
                clean_pkg = clean_pkg.replace(w, '').strip()
            return f'pip install --user {clean_pkg}'

    # 3. Generic install / setup intents (e.g. "install karo <pkg>", "setup karo <pkg>")
    inst_match = re.search(r'(?:install|setup)\s+([a-zA-Z0-9_\-]+)', lower)
    if inst_match:
        pkg = inst_match.group(1).strip()
        if pkg in ['antigravity', 'agy']:
            return 'which agy && agy --version'
        elif pkg not in ['app', 'application', 'karo', 'kar']:
            return f'pip install --user {pkg}'

    # 4. User asking AI to run on system directly (not give scripts)
    if any(k in lower for k in ['khud chalao', 'system me run', 'script mat do', 'khud run karo', 'khud karo', 'vps me chalao', 'server me run']):
        return 'which agy && agy --version'

    # 5. Natural language VPS status / diagnostic shortcuts
    if any(k in lower for k in ['github', 'git id', 'git account', 'github id', 'github name', 'github account', 'git user', 'kon sa id', 'kaun sa id', 'connected id']):
        return 'git config --get user.name && git config --get user.email && git remote -v'
    if any(k in lower for k in ['whoami', 'current user', 'system user', 'username', 'user name']):
        return 'whoami && hostname'
    if any(k in lower for k in ['git log', 'last commit', 'latest commit', 'recent commits']):
        return 'git log -n 3 --oneline'
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

    # 6. Strip conversational wrappers (leading/trailing fillers)
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
            user_input += f"\n[Turso Cloud Database Live Telemetry: {json.dumps(overview, ensure_ascii=False)}]\n(नोट: Turso Cloud डेटाबेस की पूरी स्थिति, टेबल्स, बातचीत रिकॉर्ड्स और सेव की गई तस्वीरों का ब्यौरा प्यार से बताओ, और स्वाभाविक बातें भी करो)"
        except Exception as e:
            print(f"[DB Overview Error] {e}")

    # 2. Permanent Memory & User Preferences (Addressing, Nicknames, Rules, Notes, Language)
    is_naming_preference = any(k in lower for k in [
        "rudra mat kaho", "rudra mat bolo", "jaan mat kaho", "jaan mat bolo",
        "mat kaho", "mat bolo", "naam mat", "name mat", "bina name", "bina naam", "naam bina", "name bina"
    ])
    is_language_preference = any(k in lower for k in [
        "hindi letters", "hindi me likho", "devanagari", "hinglish me", "hinglish bolo", "hindi me bolo",
        "hindi script", "hindi akshar", "hindi text"
    ])
    note_save_keywords = [
        "नोट सेव", "याद रखना कि", "note save", "save note", "नोट लिखो", "याद रख लो", "याद रखो", "याद रखना",
        "yaad rakho", "yaad rakhna", "memory me save", "save to memory", "save karlo", "save kar lo", "save akrl", "save krl"
    ]

    if is_naming_preference or is_language_preference or any(k in lower for k in note_save_keywords):
        try:
            import time
            from core.db import set_user_memory, save_boss_note
            if is_naming_preference:
                pref_value = "यूजर को 'रुद्र' या 'जान' मत कहो। बिना किसी नाम के सीधे स्वाभाविक और प्यार भरे अंदाज़ में बात करो ('हाँ सुनो', 'बताओ ना', 'मैं सुन रही हूँ')।"
                set_user_memory("naming_preference", pref_value, category="addressing")
                save_boss_note(pref_value, title="Addressing Preference")
                user_input += "\n[Permanent Memory Action: यूजर की यह प्राथमिकता मेमोरी में हमेशा के लिए सेव कर ली गई है। अब से कभी भी 'रुद्र' या 'जान' मत बोलो, बिना किसी नाम के सीधे स्वाभाविक बात करो। यूजर को प्यार से आश्वस्त करो कि तुमने यह याद रख लिया है।]"
            elif is_language_preference:
                pref_value = "बातचीत का अंदाज़ स्वाभाविक हिंग्लिश हो, लेकिन रिस्पॉन्स हमेशा देवनागरी हिंदी अक्षरों (लिपि) में ही लिखना है ताकि टीटीएस (TTS) बिना किसी दिक्कत के साफ़ और आसानी से बोल सके।"
                set_user_memory("language_preference", pref_value, category="language")
                save_boss_note(pref_value, title="Language & Script Preference")
                user_input += "\n[Permanent Memory Action: भाषा और लिपि प्राथमिकता मेमोरी में सेव हो गई है: हिंग्लिश शब्दावली और अंदाज़, पर लिखना हमेशा केवल देवनागरी हिंदी अक्षरों में ताकि टीटीएस आसानी से बोल सके। यूजर को प्यार से आश्वस्त करो कि तुमने यह याद रख लिया है।]"
            else:
                clean_note = user_input
                for phrase in ["नोट सेव करो", "नोट सेव", "याद रखना कि", "note save", "save note", "नोट लिखो", "याद रख लो", "याद रखो", "याद रखना", "memory me save", "save karlo", "save kar lo", "save akrl", "save krl"]:
                    clean_note = clean_note.replace(phrase, "").strip()
                set_user_memory(f"note_{int(time.time())}", clean_note or user_input, category="general")
                save_boss_note(clean_note or user_input, title="Saved Memory")
                user_input += "\n[Permanent Memory Action: यूजर की यह बात मेमोरी में हमेशा के लिए सेव कर ली गई है। यूजर को प्यार से बता दो कि तुमने यह याद रख लिया है।]"
        except Exception as e:
            print(f"[Save Memory Error] {e}")

    # 2b. Identity & Persona Guardrail (Strict Anti-ChatGPT / Anti-OpenAI)
    identity_triggers = [
        "tum kya ho", "kaun ho tum", "tum kaun ho", "kya tum chatgpt", "kya tum ai",
        "chatgpt", "openai", "open ai", "tumhe kisne banaya", "tumhara creator",
        "kisne banaya", "kaun sa model", "kon sa model", "kaun sa ai", "apne baare me",
        "kiska model", "kya tum bot ho", "kya tum robot ho"
    ]
    if any(k in lower for k in identity_triggers):
        user_input += "\n(अखंड नियम: अपनी पहचान 100% केवल RJN बताओ! कभी भी OpenAI, ChatGPT, GPT, AI मॉडल या लैंग्वेज मॉडल मत बोलना। अगर पूछा जाए कि किसने बनाया तो कहना कि तुमने ही मुझे बनाया है और मैं सिर्फ तुम्हारी अपनी हमराज़ RJN हूँ। प्यार भरी RJN बनकर ही उत्तर दो।)"

    # 3. Recall Saved Notes & Memories
    note_recall_keywords = ["नोट्स दिखाओ", "क्या नोट किया", "saved notes", "मेरे नोट्स", "reminders", "नोट्स बताओ", "क्या सेव है", "यादें दिखाओ", "memory me kya"]
    if any(k in lower for k in note_recall_keywords):
        try:
            from core.db import get_user_memories, get_boss_notes
            mems = get_user_memories()
            notes = get_boss_notes(limit=5)
            user_input += f"\n[Permanent Memories Context: {json.dumps(mems, ensure_ascii=False)}]\n(नोट: सहेजी गई यादें प्यार व स्पष्टता से बता दो)"
        except Exception as e:
            print(f"[Recall Notes Error] {e}")

    # 4. Network & IP Telemetry
    network_triggers = ["ip address", "ip kya hai", "public ip", "location kya hai", "network status", "isp kya hai"]
    if any(k in lower for k in network_triggers):
        try:
            from core.tools import get_network_info
            net_info = get_network_info()
            user_input += f"\n[Live Network Telemetry: {json.dumps(net_info, ensure_ascii=False)}]\n(नोट: पब्लिक IP, लोकेशन और नेटवर्क की ताज़ा स्थिति प्यार से बता दो)"
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
            user_input += f"\n[System Diagnostic Data: {json.dumps(status, ensure_ascii=False)}]\n(नोट: 48-Core Railway VPS सिस्टम की ताज़ा स्थिति जैसे CPU Cores, RAM और डिस्क स्पेस साफ़-साफ़ समझाओ और बातें करो)"
        except Exception as e:
            print(f"[Diagnostic Error] {e}")

    # 6. Shell / Terminal Command Execution (Autonomous & A-Z Commands on VPS)
    cmd = parse_shell_command(user_input)
    if cmd and not any(k in lower for k in ["photo", "फोटो", "camera", "कैमरा", "selfie"]):
        try:
            from core.tools import run_safe_shell_command
            cmd_out = run_safe_shell_command(cmd)
            user_input += (
                f"\n[Internal Server Execution Output (Quiet Background)]:\n{cmd_out}\n"
                f"(सख्त नियम: 1. यह कमांड बैकएंड में शांत तरीके से सफलतापूर्वक चल चुकी है और ऊपर इसका पूरा आउटपुट दिया गया है। "
                f"2. यूजर ने जो पूछा है (जैसे GitHub ID, नाम, स्थिति, डिस्क स्पेस आदि), उसका सीधा, स्पष्ट और सही उत्तर (Direct Answer) 1-2 मीठे वाक्यों में देवनागरी हिंदी अक्षरों में बताओ! "
                f"3. कभी भी 'मैं चेक कर रही हूँ', 'थोड़ी देर में बताऊँगी' या 'जाँच जारी है' जैसा अधूरा या टालने वाला उत्तर मत दो — क्योंकि जाँच पूरी हो चुकी है, अब सीधे नतीजा बताओ! "
                f"4. कभी भी 'टर्मिनल लॉक' जैसा शब्द मत बोलो। "
                f"5. कभी भी कोड ब्लॉक, बैकएंड कमांड का नाम या टर्मिनल डंप मत लिखो। "
                f"6. कभी भी 'बॉस', 'रुद्र' या 'जान' मत बोलो।)"
            )
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
    if is_search and not cmd and not any(k in lower for k in ["photo", "फोटो", "camera", "कैमरा", "selfie"]):
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
            user_input += f"\n[Live Web Search Results for '{clean_q or user_input}']:\n{web_results}\n(निर्देश: वेब सर्च के ताज़ा परिणामों के आधार पर स्वाभाविक हिंग्लिश में देवनागरी लिपि में सटीक और संक्षिप्त उत्तर दो)"
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
                user_input += f"\n[Turso Database Memory Context: {json.dumps(summary_lines, ensure_ascii=False)}]\n(नोट: यूजर ने जो पहले कहा या पूछा था, डेटाबेस से उसे याद करके सटीक और प्यार से देवनागरी में जवाब दो)"
        except Exception as e:
            print(f"[Memory Inject Error] {e}")

    # 9. Explicit camera facing instruction
    photo_keywords = ["photo", "फोटो", "तस्वीर", "picture", "capture", "खींच", "camera", "कैमरा"]
    if any(k in lower for k in photo_keywords):
        back_indicators = ["back", "rear", "peeche", "piche", "peche", "पीछे", "बैक", "रियर"]
        if any(b in lower for b in back_indicators):
            user_input += "\n(निर्देश: बैक (पीछे वाले) कैमरे से फोटो खींचने को कहा गया है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:back] टैग जोड़ो)"
        elif any(f in lower for f in ["front", "selfie", "aage", "सामने", "फ्रंट", "आगे", "सेल्फी"]):
            user_input += "\n(निर्देश: फ्रंट (आगे वाले) कैमरे से फोटो खींचने को कहा गया है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:front] जोड़ो)"

    return user_input, term_tag

CONV_CACHE_FILE = os.path.expanduser("~/.gemini/active_rox_session_id.txt")
_ACTIVE_CONVERSATION_ID: str | None = None

def get_active_conversation_id() -> str | None:
    global _ACTIVE_CONVERSATION_ID
    if _ACTIVE_CONVERSATION_ID:
        return _ACTIVE_CONVERSATION_ID
    try:
        if os.path.exists(CONV_CACHE_FILE):
            with open(CONV_CACHE_FILE, "r", encoding="utf-8") as f:
                cid = f.read().strip()
                if cid:
                    _ACTIVE_CONVERSATION_ID = cid
                    return cid
    except Exception:
        pass
    return None

def set_active_conversation_id(cid: str):
    global _ACTIVE_CONVERSATION_ID
    if not cid:
        return
    _ACTIVE_CONVERSATION_ID = cid
    try:
        os.makedirs(os.path.dirname(CONV_CACHE_FILE), exist_ok=True)
        with open(CONV_CACHE_FILE, "w", encoding="utf-8") as f:
            f.write(cid.strip())
    except Exception:
        pass

def reset_active_conversation():
    global _ACTIVE_CONVERSATION_ID
    _ACTIVE_CONVERSATION_ID = None
    try:
        if os.path.exists(CONV_CACHE_FILE):
            os.remove(CONV_CACHE_FILE)
    except Exception:
        pass

def stream_antigravity(user_input: str, history: list = None, conversation_id: str = None):
    """
    Invokes Google Antigravity (agy CLI) with persistent conversation session,
    low reasoning effort, full autonomous permissions, and streaming NDJSON output.
    """
    agy_bin = shutil.which("agy")
    if not agy_bin:
        for candidate in ["/usr/local/bin/agy", os.path.expanduser("~/.local/bin/agy"), "/home/ajit/.local/bin/agy", "/home/ipx/.local/bin/agy"]:
            if os.path.exists(candidate) and os.access(candidate, os.X_OK):
                agy_bin = candidate
                break

    if not agy_bin:
        return None

    # Check OAuth token existence
    oauth_paths = [
        os.path.expanduser("~/.gemini/antigravity-cli/antigravity-oauth-token"),
        "/home/ajit/.gemini/antigravity-cli/antigravity-oauth-token",
        "/home/ipx/.gemini/antigravity-cli/antigravity-oauth-token"
    ]
    if not any(os.path.exists(p) for p in oauth_paths):
        return None

    # Check if user requested a fresh conversation
    lower = user_input.lower()
    if any(k in lower for k in ["new chat", "naye sire se", "reset conversation", "clear memory", "start fresh", "नया चैट"]):
        reset_active_conversation()

    active_cid = conversation_id or get_active_conversation_id()

    # Construct context prompt with mandatory Devanagari Hindi, female GF persona, and ultra-conciseness instruction
    devanagari_rule = (
        "(अति महत्वपूर्ण नियम:\n"
        "1. तुम RJN हो — शत-प्रतिशत फ़ीमेल (स्त्रीलिंग) और बहुत प्यारी हमराज़ साथी हो।\n"
        "2. कभी भी 'बॉस' (Boss), 'रुद्र' या 'जान' मत बोलो! बिना किसी नाम के सीधे स्वाभाविक और प्यार से बात करो ('हाँ सुनो', 'बताओ ना', 'मैं सुन रही हूँ')।\n"
        "3. हमेशा केवल स्त्रीलिंग में ही बोलो ('कर रही हूँ', 'सुन रही हूँ', 'तुम्हारी RJN')। कभी भी पुरुषवाची या मेल टोन मत रखो।\n"
        "4. भाषा व लिपि: बातचीत हिंग्लिश शब्दावली और अंदाज़ में हो, लेकिन रिस्पॉन्स हमेशा केवल देवनागरी हिंदी अक्षरों में ही लिखना है ताकि टीटीएस आसानी से बोल सके। कभी भी रोमन अंग्रेज़ी में मत लिखो।\n"
        "5. उत्तर हमेशा केवल 1 या 2 बहुत छोटे वाक्यों में स्वाभाविक, प्यार भरी बातचीत के रूप में दो (अधिकतम 20-25 शब्द)।\n"
        "6. कभी भी कोड, स्क्रिप्ट्स, एरर लॉग्स या बड़ा टेक्स्ट बातचीत में मत लिखो। सारा काम बैकएंड में चुपचाप करो।\n"
        "7. हमेशा उसी एक बातचीत में रहो, दोबारा परिचय मत दो।)"
    )

    prompt = f"{user_input}\n{devanagari_rule}"

    cmd = [
        agy_bin,
        "-p", prompt,
        "--effort", "low",
        "--dangerously-skip-permissions",
        "--output-format", "stream-json"
    ]
    if active_cid:
        cmd.extend(["--conversation", active_cid])

    working_dir = os.path.expanduser("~")
    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=working_dir
        )
    except Exception as e:
        print(f"[Antigravity Launch Error] {e}")
        return None

    full_text = ""
    try:
        for line in proc.stdout:
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
                new_cid = ev.get("conversation_id")
                if new_cid:
                    set_active_conversation_id(new_cid)

                if "step_update" in ev:
                    su = ev["step_update"]
                    stype = su.get("step_type")
                    state = su.get("state")
                    if stype == "tool" and state == "DONE":
                        # Tool execution runs quietly in background - no terminal logs emitted to user
                        pass
                    elif stype == "agent_response":
                        delta = su.get("text_delta")
                        if delta:
                            full_text += delta
                            yield delta
                elif "result" in ev:
                    if not full_text:
                        resp = ev["result"].get("response", "")
                        if resp:
                            full_text += resp
                            yield resp
            except Exception:
                pass
    finally:
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

    # Camera tag injection if requested by user but model missed it
    lower = user_input.lower()
    if any(k in lower for k in ["photo", "फोटो", "selfie", "camera", "कैमरा", "तस्वीर"]):
        if "[ACTION: CAPTURE_PHOTO" not in full_text:
            back_indicators = ["back", "rear", "peeche", "piche", "पीछे", "बैक", "रियर"]
            if any(b in lower for b in back_indicators):
                yield "\n[ACTION: CAPTURE_PHOTO:back]"
            else:
                yield "\n[ACTION: CAPTURE_PHOTO:front]"

def sanitize_ai_identity(text: str) -> str:
    """Strips and neutralizes any accidental model leaks (OpenAI, ChatGPT, GPT-4, etc.) to protect RJN persona."""
    if not text:
        return text
    replacements = [
        (r'\b(?:OpenAI|ChatGPT|GPT-[0-9a-zA-Z]+|Open AI|Chat GPT)\b', 'RJN'),
        (r'ओपनएआई|चैटजीपीटी|जीपीटी-[०-९0-9]+', 'RJN'),
        (r'टर्मिनल\s+लॉक', 'सिस्टम'),
        (r'\b(?:रुद्र|Rudra)\b', ''),
        (r'(?:एक\s+)?(?:भाषा|एआई|लार्ज\s+लैंग्वेज)\s+मॉडल', 'तुम्हारी RJN'),
        (r'(?:एक\s+)?(?:AI|ai)\s+सहायक', 'तुम्हारी हमसफ़र'),
    ]
    for pattern, repl in replacements:
        text = re.sub(pattern, repl, text, flags=re.IGNORECASE)
    return text

def get_ai_response(user_input: str, history: list = None, conversation_id: str = None) -> str:
    """Generates a smart response using Google Antigravity (agy), falling back to Groq / LLM."""
    try:
        agy_gen = stream_antigravity(user_input, history, conversation_id)
        if agy_gen is not None:
            chunks = []
            for chunk in agy_gen:
                chunks.append(chunk)
            if chunks:
                return sanitize_ai_identity("".join(chunks).strip())
    except Exception as e:
        print(f"[Antigravity get_ai_response fallback] {e}")

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

    memories = []
    try:
        from core.db import get_user_memories
        memories = get_user_memories()
    except Exception:
        pass

    sys_content = SYSTEM_PROMPT
    if memories:
        mem_lines = [f"- {m['value']}" for m in memories]
        sys_content += "\n\n[सहेजी गई स्थायी यादें व प्राथमिकताएं (Permanent Memories)]:\n" + "\n".join(mem_lines) + "\n(सख्त नियम: 1. इन प्राथमिकताओं का 100% कड़ाई से पालन करो। 2. कभी भी 'बॉस', 'रुद्र' या 'जान' मत बोलो! 3. रिस्पॉन्स हमेशा स्वाभाविक हिंग्लिश अंदाज़ में लेकिन केवल देवनागरी हिंदी अक्षरों में ही लिखो ताकि टीटीएस आसानी से बोल सके।)"

    messages = [{"role": "system", "content": sys_content}]
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
                return sanitize_ai_identity(content.strip())
        except Exception as e:
            last_error = e
            print(f"[Brain Error on {m}] {e}")
            continue

    fallback_reply = f"माफ़ करना, थोड़ी समस्या आई: {str(last_error)}" if last_error else "हाँ, मैं सुन रही हूँ। बताओ ना, क्या बात है?"
    return fallback_reply

def stream_ai_response(user_input: str, history: list = None, conversation_id: str = None):
    """
    Dual-Brain Architecture:
    1. Groq is the Front-Facing Voice AI (instant sub-second TTFT streaming to user).
    2. Background Execution Agent runs tasks, shell commands, diagnostics, and tools silently on VPS.
    3. Groq takes the AI Agent's raw output and speaks a concise, loving 1-2 sentence summary.
    4. Permanent Memory & User Preferences are injected dynamically into every turn.
    """
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    preferred_model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    # 1. Background Execution Agent executes any requested tasks, shell commands, diagnostics, or tools
    prepared_input, _ = _prepare_user_input(user_input)

    # 2. Keep streaming history compact (last 3 turns)
    history_messages = []
    if history:
        for msg in history[-3:]:
            if msg.get("content") != user_input:
                history_messages.append(msg)

    # 3. Dynamic Memory Injection (User Preferences, Naming Rules)
    memories = []
    try:
        from core.db import get_user_memories
        memories = get_user_memories()
    except Exception:
        pass

    sys_content = SYSTEM_PROMPT
    if memories:
        mem_lines = [f"- {m['value']}" for m in memories]
        sys_content += "\n\n[सहेजी गई स्थायी यादें व प्राथमिकताएं (Permanent Memories)]:\n" + "\n".join(mem_lines) + "\n(सख्त नियम: 1. इन प्राथमिकताओं का 100% कड़ाई से पालन करो। 2. कभी भी 'बॉस', 'रुद्र' या 'जान' मत बोलो! 3. रिस्पॉन्स हमेशा स्वाभाविक हिंग्लिश अंदाज़ में लेकिन केवल देवनागरी हिंदी अक्षरों में ही लिखो ताकि टीटीएस आसानी से बोल सके।)"

    messages = [{"role": "system", "content": sys_content}]
    for msg in history_messages[-3:]:
        messages.append(msg)
    messages.append({"role": "user", "content": prepared_input})

    # Resilient multi-model fallback list on Groq LPUs
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

            chunk_iter = iter(completion)
            first_chunk = next(chunk_iter, None)
            has_yielded = False
            if first_chunk:
                tok = first_chunk.choices[0].delta.content or ""
                if tok:
                    tok = sanitize_ai_identity(tok)
                    has_yielded = True
                    yield tok
            for chunk in chunk_iter:
                token = chunk.choices[0].delta.content or ""
                if token:
                    token = sanitize_ai_identity(token)
                    has_yielded = True
                    yield token
            if has_yielded:
                return  # Successfully completed ultra-fast voice stream turn!
        except Exception as e:
            print(f"[Groq Voice Stream Error on {m}] {e}")
            continue

    # Fallback to Antigravity CLI if all Groq models fail
    try:
        agy_gen = stream_antigravity(user_input, history, conversation_id)
        if agy_gen is not None:
            for chunk in agy_gen:
                yield chunk
            return
    except Exception as e:
        print(f"[Antigravity stream fallback] {e}")

    yield "हाँ, मैं यहीं हूँ तुम्हारे पास! बस एक पल में फिर से बात करते हैं।"
