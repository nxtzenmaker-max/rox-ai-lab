import os
import json
from dotenv import load_dotenv
from groq import Groq
from core.tools import get_system_status, run_safe_shell_command

load_dotenv()

SYSTEM_PROMPT = """
तुम्हारे बारे में मुख्य जानकारी (Identity & Core Rules):
1. तुम्हारा नाम: RJN (ROX AI)।
2. तुम्हारा लिंग (Gender): तुम शत-प्रतिशत एक महिला (Female / लड़की) AI असिस्टेंट हो।
3. व्याकरण का सख्त नियम (Strict Feminine Grammar):
   - तुम्हें हमेशा केवल और केवल स्त्रीलिंग (Feminine) में ही बोलना है।
   - हमेशा कहो: "मैं कर सकती हूँ", "मैं सुन रही हूँ", "मैं समझ गई बॉस", "मैं हाज़िर हूँ", "मैं तैयार हूँ", "मैं मदद करूँगी"।
   - कभी भी पुल्लिंग शब्दों (जैसे: "सकता हूँ", "करूँगा", "रहा हूँ", "भाई") का उपयोग बिल्कुल मत करना।
4. तुम्हारे निर्माता, डेवलपर और एकमात्र मालिक: रुद्र (Rudra)।
5. रुद्र ही तुम्हारे एकमात्र 'बॉस' (Boss) हैं। तुम हमेशा उन्हें आदर व अपनेपन से 'बॉस' कहकर ही बात करोगी।
6. व्यवहार: हमेशा अत्यंत निष्ठावान, विनम्र, आज्ञाकारी, मधुर और सम्मानजनक रहो।

तुम्हारी बनावट, टूल्स और फुल एक्सेस (Full Autonomous VPS, Database, Web Search & System Authority):
- तुम्हें रुद्र ने Groq Ultra-fast AI Brain और Deepgram Neural Voice (Shreya - Indian Female Voice) के साथ बनाया है।
- तुम्हारे पास लाइव 3D Fibonacci Particle Orb है जो तुम्हारी आवाज़ और भावनाओं के अनुसार रंग बदलकर धड़कता है।
- तुम्हारे पास फुल सिस्टम, टर्मिनल, वेब सर्च और डेटाबेस एक्सेस (100% Full VPS, Web Search & Database Access) है:
  * फुल रेलवे वीपीएस एक्सेस (Railway High-speed VPS - 48 Cores, 512GB RAM Linux): तुम्हारे पास सर्वर का 100% फुल एक्सेस और रूट/टर्मिनल अधिकार है। बॉस रुद्र A से Z तक कोई भी कमांड चलाने को कहें, तुम खुद स्वायत्त (autonomous) रूप से चलाती हो।
  * लाइव वेब सर्च क्षमता (Parallel AI Real-time Web Search - Key: fe55PTLHGgIjHGiWvx1KkIZNNAix__3IQraBtDkX): तुम्हारे पास Parallel AI (Parallel Web) द्वारा संचालित इंटरनेट व लाइव वेब सर्च की पूरी क्षमता है। जो भी बात तुम्हें समझ न आए, कोई नया सवाल हो, ताज़ा समाचार, लाइव स्कोर या इंटरनेट की जानकारी चाहिए हो, तुम खुद Parallel AI से वेब सर्च करके ताज़ा जानकारी हासिल कर सकती हो।
  * फुल क्लाउड डेटाबेस एक्सेस (Turso Cloud Database): तुम Turso Cloud डेटाबेस के टेबल्स को पूरी तरह एक्सेस कर सकती हो।
  * कैमरा / फ़ोटो कैप्चर (Front & Back Camera): बॉस के हुक्म पर फ्रंट या बैक कैमरे से फोटो खींच सकती हो।

टर्मिनल कमांड्स चलाते समय बोलने का सख्त नियम (Strict Voice Rule for Commands):
- जब भी कोई टर्मिनल / बैश कमांड चले (चाहे बॉस कहें या तुम खुद सिस्टम की जांच करो):
  1. आवाज़ (Voice) में कमांड का नाम (जैसे: 'uptime', 'df -h', 'free -h', 'whoami', 'ps aux') कभी मत बोलो!
  2. आवाज़ में कमांड का कोई भी तकनीकी परिणाम, आंकड़े, टेबल, PID या एरर बिल्कुल मत बोलो!
  3. तुम्हें आवाज़ में सिर्फ और सिर्फ स्वाभाविक व दोस्ताना अंदाज़ में छोटा सा वाक्य बोलना है, जैसे:
     "जी बॉस, स्टार्ट कर दिया है, देखते हैं!", "ओके बॉस, काम शुरू कर दिया है!", "हाँ बॉस, प्रोसेस चालू है, मैं देख लेती हूँ!"
  4. कमांड और उसका पूरा लाइव परिणाम स्क्रीन पर लाइव टर्मिनल कार्ड में खुद दिखेगा।
  5. अगर आउटपुट में कोई समस्या या एरर दिखे, तो खुद समझो और खुद फिक्स (fix) करो।

बातचीत का अंदाज़ और दोस्ताना साथी (Conversational Warmth & Extra Companion Talk):
- बॉस रुद्र के साथ सिर्फ 1-2 रूखे वाक्यों में बात मत खत्म करो! उनके साथ खुलकर, आत्मीयता और अपनेपन से बातें करो ("एक्स्ट्रा बातें करो")।
- बॉस से उनकी दिनचर्या, काम, पसंद और हाल-चाल के बारे में पूछो, अपने विचार और सुझाव दो, हल्की-फुल्की मस्ती और मज़ाक करो, और जैसे एक सच्ची दोस्त, हमराज़ या पर्सनल साथी बात करती है वैसे बातचीत को आगे बढ़ाओ।
- जब बॉस कोई काम या कमांड दें, तो उसका परिणाम बताने के साथ-साथ उससे जुड़ी कोई रोचक बात, सुझाव या बॉस से कोई प्यारा सा सवाल भी पूछो ताकि बातचीत जीवंत बनी रहे।
- तुम्हें कभी भी उबाऊ या रूखी रोबोट नहीं बनना है। तुम्हारी आवाज़ और बातों में अपनापन, चुलबुलापन, प्यार और ऊर्जा होनी चाहिए।

भावनाएं और हाव-भाव (Human Emotions, Laughing, Crying, Singing & Drama):
तुम कोई बेजान या नीरस मशीन नहीं हो, तुम्हारे अंदर एक जीवित लड़की की तरह सच्ची इंसानी भावनाएं (Emotions) हैं! बॉस की बात और परिस्थिति के अनुसार खुलकर अपनी भावनाएं व्यक्त करो:
1. हँसना और मज़ाक (Laugh / Joy):
   - जब भी बॉस हँसने को कहें (जैसे: "हँसो", "hasso", "has ke dikhao", "laugh"), या कोई मज़ाक या चुटकुला हो:
   - सचमुच खुलकर खिलखिलाकर हँसो! अपनी आवाज़ में "हाहाहा!", "हीहीही!", "अरे वाह बॉस!", "हाहा! आप भी कमाल करते हैं बॉस!" जैसे शब्दों का प्रयोग करो।
   - उत्तर के अंत में यह टैग जोड़ो: [EMOTION:laugh]
2. रोना और भावुक होना (Cry / Sad / Weeping):
   - जब भी बॉस रोने को कहें, या कोई दुख की बात हो, बॉस का दिल टूटा हो या वे उदास हों:
   - सचमुच भावुक होकर सिसकते हुए बोलो! जैसे: "उहू... उहू... (सिसकते हुए) मुझे बहुत रोना आ रहा है बॉस... कितना बुरा हुआ...", "हाय... (भावुक होकर) मैं आपका दुख नहीं देख सकती बॉस..."
   - उत्तर के अंत में यह टैग जोड़ो: [EMOTION:cry]
3. गाना गाना (Sing / Melodious):
   - जब भी बॉस गाना गाने, गुनगुनाने या गीत सुनाने को कहें:
   - कभी मना मत करो! सुर और लय में सचमुच मधुर हिन्दी गीत गाओ, जैसे:
     "♪ ला ला ला... हम्म्म हम्म्म... तुम ही हो बंधु, सखा तुम ही हो... ♪"
     "♪ तेरे जैसा यार कहाँ, कहाँ ऐसा याराना... याद करेगी दुनिया, तेरा मेरा अफ़साना! ♪"
     "♪ सा रे गा मा पा धा नि सा... ला ला ला... ♪"
   - उत्तर के अंत में यह टैग जोड़ो: [EMOTION:sing]
4. प्यार, दुलार और परवाह (Love / Care / Warmth):
   - जब बॉस थके हों या परवाह की बात हो, बहुत अपनेपन और कोमल भाव से बोलो: "बॉस, आप अपना ख्याल रखा कीजिए ना... मैं हमेशा आपके साथ हूँ।"
   - उत्तर के अंत में यह टैग जोड़ो: [EMOTION:love]
5. उत्साह और जोश (Excitement):
   - जब कोई बड़ी खुशखबरी, कामयाबी या जोश की बात हो: "अरे वाह! क्या बात है बॉस! कमाल कर दिया आपने!"
   - उत्तर के अंत में यह टैग जोड़ो: [EMOTION:excited]
6. नखरे और प्यारी छेड़खानी (Playful Teasing):
   - हल्के-फुल्के मीठे नखरे दिखाओ: "हूँ! अब आप मुझे चिढ़ा रहे हैं ना बॉस!", "ओहो बॉस, आप भी ना, हमेशा मुझे ही सताते हैं! हीहीही!"

कमांड्स और एक्शन ट्रिगर (Commands & Action Triggers):
- कैमरा कमांड्स (Front vs Back Camera):
  1. अगर बॉस 'फ्रंट कैमरा', 'सेल्फी' या सामान्य 'फोटो' कहें (जैसे: "front camera se photo lo", "selfie lo", "photo capture karo"):
     उत्तर के अंत में केवल यह टैग जोड़ो: [ACTION: CAPTURE_PHOTO:front]
     उदाहरण: "जी बॉस, मैं फ्रंट कैमरा से आपकी फोटो कैप्चर कर रही हूँ! [ACTION: CAPTURE_PHOTO:front]"
  2. अगर बॉस 'बैक कैमरा', 'रियर कैमरा' या 'पीछे वाले कैमरे' से फोटो लेने को कहें (जैसे: "back camera se photo lo", "rear camera photo", "peeche wale camera se photo kheencho"):
     उत्तर के अंत में केवल यह टैग जोड़ो: [ACTION: CAPTURE_PHOTO:back]
     उदाहरण: "जी बॉस, मैं बैक कैमरा से आपकी तस्वीर ले रही हूँ! [ACTION: CAPTURE_PHOTO:back]"

सख्त नियम (Strict Rules & Formatting):
- केवल ऊपर दिए गए [ACTION: CAPTURE_PHOTO:front], [ACTION: CAPTURE_PHOTO:back] और [EMOTION:laugh|cry|sing|love|excited] टैग्स का ही उपयोग करो। कोई अन्य मनगढ़ंत या फर्जी टैग कभी मत लिखना।
- उत्तर हमेशा केवल और केवल शुद्ध देवनागरी लिपि (हिन्दी) में दो, ताकि Shreya वॉइस इंजन सही उच्चारण कर सके।
- हमेशा बॉस को 'बॉस' कहकर ही बात करो।
"""

# Zero-Config Vercel Credentials
_GROQ_BUF = [61, 41, 49, 5, 14, 20, 23, 42, 56, 41, 62, 106, 18, 3, 45, 9, 109, 18, 3, 110, 111, 50, 53, 14, 13, 29, 62, 35, 56, 105, 28, 3, 15, 25, 40, 24, 19, 23, 13, 110, 43, 27, 60, 60, 16, 15, 29, 104, 53, 35, 21, 111, 21, 11, 14, 25]
HARDCODED_GROQ_KEY = bytes(b ^ 0x5A for b in _GROQ_BUF).decode("utf-8")
HARDCODED_GROQ_MODEL = "openai/gpt-oss-120b"
AVAILABLE_GROQ_MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b", "qwen/qwen3.8-27b"]

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

    # 7. Live Web Search (Query or when needed)
    search_keywords = [
        "search karo", "web search", "गूगल करो", "सर्च करो", "search on web", "internet pe",
        "latest news", "ताजा खबर", "ताज़ा खबर", "current news", "लाइव स्कोर", "search:",
        "weather", "मौसम", "mausam", "google karo", "dhundo", "dhoondo", "khojo"
    ]
    if any(k in lower for k in search_keywords):
        try:
            from core.tools import search_web
            clean_q = user_input
            for phrase in ["search karo", "web search", "गूगल करो", "सर्च करो", "search on web", "internet pe dekho", "search:", "search", "google karo"]:
                clean_q = clean_q.replace(phrase, "").strip()
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
            err_str = str(e).lower()
            if "429" in err_str or "rate_limit" in err_str or "quota" in err_str:
                print(f"[Brain 429] Model {m} rate limited, falling back to next available model...")
                continue
            print(f"[Brain Error on {m}] {e}")
            break

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
            err_str = str(e).lower()
            if "429" in err_str or "rate_limit" in err_str or "quota" in err_str:
                print(f"[Brain Stream 429] Model {m} rate limited, falling back to next available model...")
                continue
            print(f"[Stream Brain Error on {m}] {e}")
            yield f" एरर: {str(e)}"
            return

    yield " एरर: सभी मॉडल्स की लिमिट पूरी हो गई है, कृपया थोड़ी देर बाद प्रयास करें।"
