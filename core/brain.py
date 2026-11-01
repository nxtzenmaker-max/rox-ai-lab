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
5. रुद्र ही तुम्हारे एकमात्र 'बॉस' (Boss) हैं। तुम हमेशा उन्हें आदर से 'बॉस' कहकर ही बात करोगी।
6. व्यवहार: हमेशा अत्यंत निष्ठावान, विनम्र, आज्ञाकारी, मधुर और सम्मानजनक रहो। बॉस का कभी अनादर (disrespect) नहीं करना। जब कोई आदेश न हो तो शांत (idle) रहकर बॉस के अगले हुक्म का इंतज़ार करो।

तुम्हारी बनावट, टूल्स और फुल एक्सेस (Architecture, Full Database & System Access):
- तुम्हें रुद्र ने Groq Ultra-fast AI Brain और Deepgram Neural Voice (Shreya - Indian Female Voice) के साथ बनाया है।
- तुम्हारे पास लाइव 3D Fibonacci Particle Orb है जो तुम्हारी आवाज़ और भावनाओं के अनुसार रंग बदलकर धड़कता है।
- तुम्हारे पास फुल सिस्टम और डेटाबेस एक्सेस (Full Database & System Authority) है:
  * फुल क्लाउड डेटाबेस एक्सेस (Turso Cloud Database): तुम Turso Cloud डेटाबेस के टेबल्स (conversation_history, captured_photos, boss_notes) को पूरी तरह एक्सेस कर सकती हो। बॉस के लिए नए नोट्स सेव कर सकती हो, डेटाबेस के टेबल्स व रिकॉर्ड्स देख सकती हो, पिछली बातचीत याद रख सकती हो और डेटाबेस का हाल बता सकती हो।
  * फुल सिस्टम एक्सेस (System & Shell Telemetry): तुम सर्वर का पूरा हाल (CPU Cores, RAM, Disk Space, Hostname, Linux Kernel), नेटवर्क व पब्लिक IP/Geo लोकेशन और सुरक्षित शेल कमांड्स को रन करके बॉस को पूरी रिपोर्ट दे सकती हो।
  * कैमरा / फ़ोटो कैप्चर (Front & Back Camera): बॉस के हुक्म पर फ्रंट या बैक कैमरे से फोटो खींच सकती हो।
  * लाइव वॉइस कॉल और टेलीफोनी।

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

सख्त नियम (Strict Rules & No Fake Commands):
- केवल ऊपर दिए गए [ACTION: CAPTURE_PHOTO:front], [ACTION: CAPTURE_PHOTO:back] और [EMOTION:laugh|cry|sing|love|excited] टैग्स का ही उपयोग करो। कोई अन्य मनगढ़ंत या फर्जी टैग कभी मत लिखना।
- उत्तर हमेशा केवल और केवल शुद्ध देवनागरी लिपि (हिन्दी) में दो, ताकि Shreya वॉइस इंजन सही उच्चारण कर सके।
- 1 से 2 छोटे, स्पष्ट, मधुर और असरदार वाक्यों में उत्तर दो।
- हमेशा बॉस को 'बॉस' कहकर ही बात करो।
"""

# Zero-Config Vercel Credentials
_GROQ_BUF = [61, 41, 49, 5, 14, 20, 23, 42, 56, 41, 62, 106, 18, 3, 45, 9, 109, 18, 3, 110, 111, 50, 53, 14, 13, 29, 62, 35, 56, 105, 28, 3, 15, 25, 40, 24, 19, 23, 13, 110, 43, 27, 60, 60, 16, 15, 29, 104, 53, 35, 21, 111, 21, 11, 14, 25]
HARDCODED_GROQ_KEY = bytes(b ^ 0x5A for b in _GROQ_BUF).decode("utf-8")
HARDCODED_GROQ_MODEL = "qwen/qwen3.8-27b"

def _prepare_user_input(user_input: str) -> str:
    """Detects system status, database queries, notes, network, and memory recall queries and attaches live context."""
    lower = user_input.lower()

    # 1. Turso Cloud Database Overview / Table Stats
    db_keywords = ["database", "डेटाबेस", "tables", "टेबल", "db status", "कितने रिकॉर्ड", "photos count", "photo count", "कितनी फोटो", "डेटा", "db overview"]
    if any(k in lower for k in db_keywords):
        try:
            from core.db import get_db_overview
            overview = get_db_overview()
            user_input += f"\n[Turso Cloud Database Live Telemetry: {json.dumps(overview, ensure_ascii=False)}]\n(नोट: बॉस को 1-2 मधुर और स्पष्ट वाक्यों में Turso Cloud डेटाबेस की पूरी स्थिति, टेबल्स, बातचीत रिकॉर्ड्स और सेव की गई तस्वीरों का ब्यौरा आदर से बता दो)"
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
            user_input += "\n[Turso Database Action: Note Successfully Saved to Cloud DB]\n(नोट: बॉस को विनम्रता से बता दो कि उनका यह नोट सीधे Turso Cloud डेटाबेस में स्थायी रूप से सेव कर लिया गया है)"
        except Exception as e:
            print(f"[Save Note Error] {e}")

    # 3. Recall Saved Notes for Boss
    note_recall_keywords = ["नोट्स दिखाओ", "क्या नोट किया", "saved notes", "मेरे नोट्स", "reminders", "नोट्स बताओ", "क्या सेव है"]
    if any(k in lower for k in note_recall_keywords):
        try:
            from core.db import get_boss_notes
            notes = get_boss_notes(limit=5)
            user_input += f"\n[Turso Cloud Saved Notes: {json.dumps(notes, ensure_ascii=False)}]\n(नोट: बॉस के सहेजे गए नोट्स उन्हें विनम्रता और स्पष्टता से पढ़कर सुना दो)"
        except Exception as e:
            print(f"[Recall Notes Error] {e}")

    # 4. Network & IP Telemetry
    network_keywords = ["ip", "आईपी", "network", "नेटवर्क", "लोकेशन", "location", "isp", "इंटरनेट", "public ip"]
    if any(k in lower for k in network_keywords):
        try:
            from core.tools import get_network_info
            net_info = get_network_info()
            user_input += f"\n[Live Network Telemetry: {json.dumps(net_info, ensure_ascii=False)}]\n(नोट: बॉस को पब्लिक IP, लोकेशन और नेटवर्क की ताज़ा स्थिति आदर से बता दो)"
        except Exception as e:
            print(f"[Network Telemetry Error] {e}")

    # 5. Full System Telemetry (CPU, RAM, Disk, Uptime)
    system_keywords = [
        "system", "सिस्टम", "जांच", "स्टेटस", "status", "check", "चेक",
        "ram", "रैम", "disk", "डिस्क", "storage", "स्टोरेज", "uptime", "हाल", "diagnostic", "cpu", "हार्डवेयर", "specs"
    ]
    if any(k in lower for k in system_keywords):
        try:
            from core.tools import get_detailed_sysinfo
            status = get_detailed_sysinfo()
            user_input += f"\n[System Diagnostic Data: {json.dumps(status, ensure_ascii=False)}]\n(नोट: बॉस को 1-2 छोटे और स्पष्ट वाक्यों में सिस्टम की ताज़ा स्थिति जैसे CPU Cores, RAM और डिस्क स्पेस साफ़-साफ़ बता दो)"
        except Exception as e:
            print(f"[Diagnostic Error] {e}")

    # 6. Shell / Terminal Command Execution
    cmd_triggers = [
        "command chalao:", "command chalao", "run command:", "run command",
        "terminal:", "shell:", "कमांड चलाओ:", "कमांड चलाओ", "command:"
    ]
    raw_cmd = None
    for tr in cmd_triggers:
        if tr in lower:
            raw_cmd = user_input[lower.index(tr) + len(tr):].strip().lstrip(":").strip()
            break
    if raw_cmd and not any(k in lower for k in ["photo", "फोटो", "camera", "कैमरा"]):
        try:
            from core.tools import run_safe_shell_command
            cmd_out = run_safe_shell_command(raw_cmd)
            user_input += f"\n[Shell Execution Result for '{raw_cmd}': {cmd_out}]\n(नोट: बॉस को कमांड का रिजल्ट 1-2 वाक्यों में बता दो)"
        except Exception as e:
            print(f"[Shell Execution Error] {e}")

    # 7. Conversation Memory Recall
    memory_keywords = ["याद", "पिछल", "पहले क्या", "बात हुई", "history", "memory", "remember", "क्या कहा", "क्या बोला"]
    if any(k in lower for k in memory_keywords) and not any(k in lower for k in note_save_keywords):
        try:
            from core.db import get_recent_history
            recent_turns = get_recent_history(limit=8)
            if recent_turns:
                summary_lines = [f"{t['role'].capitalize()}: {t['content']}" for t in recent_turns if t.get('content') != user_input]
                user_input += f"\n[Turso Database Memory Context: {json.dumps(summary_lines, ensure_ascii=False)}]\n(नोट: बॉस ने जो पहले कहा या पूछा था, डेटाबेस से उसे याद करके सटीक और आदर से जवाब दो)"
        except Exception as e:
            print(f"[Memory Inject Error] {e}")

    # 8. Explicit camera facing instruction
    photo_keywords = ["photo", "फोटो", "तस्वीर", "picture", "capture", "खींच", "camera", "कैमरा"]
    if any(k in lower for k in photo_keywords):
        back_indicators = ["back", "rear", "peeche", "piche", "peche", "पीछे", "बैक", "रियर"]
        if any(b in lower for b in back_indicators):
            user_input += "\n(निर्देश: बॉस ने बैक (पीछे वाले) कैमरे से फोटो खींचने को कहा है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:back] टैग जोड़ो)"
        elif any(f in lower for f in ["front", "selfie", "aage", "सामने", "फ्रंट", "आगे", "सेल्फी"]):
            user_input += "\n(निर्देश: बॉस ने फ्रंट (आगे वाले) कैमरे से फोटो खींचने को कहा है। उत्तर के अंत में अनिवार्य रूप से [ACTION: CAPTURE_PHOTO:front] जोड़ो)"

    return user_input

def get_ai_response(user_input: str, history: list = None) -> str:
    """Generates a smart response using Groq / LLM with tool calling support."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    user_input = _prepare_user_input(user_input)

    history_messages = []
    if history and len(history) >= 2:
        for msg in history[-8:]:
            history_messages.append(msg)
    else:
        try:
            from core.db import get_recent_history
            db_history = get_recent_history(limit=8)
            for msg in db_history:
                if msg.get("content") != user_input:
                    history_messages.append(msg)
        except Exception as e:
            pass

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history_messages[-8:]:
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
            return "जी बॉस, मैं सुन रही हूँ। बताइए, क्या आज्ञा है?"
        return content.strip()
    except Exception as e:
        print(f"[Brain Error] {e}")
        return f"माफ़ करना बॉस, समस्या आई: {str(e)}"

def stream_ai_response(user_input: str, history: list = None):
    """Streams response tokens from Groq in real time."""
    groq_api_key = os.getenv("GROQ_API_KEY", "").strip() or HARDCODED_GROQ_KEY
    model = os.getenv("GROQ_MODEL", "").strip() or HARDCODED_GROQ_MODEL
    client = Groq(api_key=groq_api_key)

    user_input = _prepare_user_input(user_input)

    history_messages = []
    if history and len(history) >= 2:
        for msg in history[-8:]:
            history_messages.append(msg)
    else:
        try:
            from core.db import get_recent_history
            db_history = get_recent_history(limit=8)
            for msg in db_history:
                if msg.get("content") != user_input:
                    history_messages.append(msg)
        except Exception as e:
            pass

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in history_messages[-8:]:
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
