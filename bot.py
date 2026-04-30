"""
YomnaBot — يشتغل مرة واحدة عن طريق GitHub Actions
كل شغلة بتعمل المهمة المطلوبة وبتحفظ التقدم في state.json
"""

import os
import json
import sys
import requests
from datetime import datetime
import pytz

# ─────────────────────────────────────────────
#  الإعدادات
# ─────────────────────────────────────────────
BOT_TOKEN    = os.environ["BOT_TOKEN"]
CHAT_ID      = os.environ.get("CHAT_ID", "-1003844022713")
TOPIC_ID     = os.environ.get("TOPIC_ID", "33")
RELEASE_BASE     = os.environ.get("RELEASE_BASE", "")
RELEASE_BASE_MP3 = os.environ.get("RELEASE_BASE_MP3", RELEASE_BASE)
CAIRO_TZ     = pytz.timezone("Africa/Cairo")
TOTAL_FILES  = 604
STATE_FILE   = "state.json"
BASE_URL     = f"https://api.telegram.org/bot{BOT_TOKEN}"

# ─────────────────────────────────────────────
#  State
# ─────────────────────────────────────────────
def load_state() -> dict:
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"current_file": 1}

def save_state(state: dict):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)
    print(f"💾 حُفظ التقدم: ملف رقم {state['current_file']}")

# ─────────────────────────────────────────────
#  Telegram helpers
# ─────────────────────────────────────────────
def _base_params() -> dict:
    return {"chat_id": CHAT_ID, "message_thread_id": TOPIC_ID}

def send_text(text: str):
    r = requests.post(
        f"{BASE_URL}/sendMessage",
        data={**_base_params(), "text": text, "parse_mode": "HTML"},
    )
    print(f"📨 نص: {r.status_code} | {r.json().get('description','OK')}")

def send_document_url(url: str, caption: str = ""):
    print(f"⬇️  تحميل PDF...")
    r = requests.get(url, allow_redirects=True)
    filename = url.split("/")[-1]
    files = {"document": (filename, r.content, "application/pdf")}
    r2 = requests.post(
        f"{BASE_URL}/sendDocument",
        data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
        files=files,
    )
    print(f"📄 PDF: {r2.status_code} | {r2.json().get('description','OK')}")

def send_audio_url(url: str, caption: str = ""):
    print(f"⬇️  تحميل MP3...")
    r = requests.get(url, allow_redirects=True)
    filename = url.split("/")[-1]
    files = {"audio": (filename, r.content, "audio/mpeg")}
    r2 = requests.post(
        f"{BASE_URL}/sendAudio",
        data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
        files=files,
    )
    print(f"🎵 MP3: {r2.status_code} | {r2.json().get('description','OK')}")

def send_photo_file(path: str, caption: str = ""):
    with open(path, "rb") as photo:
        r = requests.post(
            f"{BASE_URL}/sendPhoto",
            data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
            files={"photo": photo},
        )
    print(f"🖼️ صورة: {r.status_code} | {r.json().get('description','OK')}")

# ─────────────────────────────────────────────
#  Progress bar
# ─────────────────────────────────────────────
def progress_bar(current: int, total: int, length: int = 10) -> str:
    filled = int((current / total) * length)
    return "🟩" * filled + "⬜" * (length - filled)

# ─────────────────────────────────────────────
#  المهام
# ─────────────────────────────────────────────
def task_daily_files():
    """5:30 ص — PDF + MP3"""
    state = load_state()
    n     = state["current_file"]
    num   = f"{n:03d}"

    pct = round((n / TOTAL_FILES) * 100, 1)
    bar = progress_bar(n, TOTAL_FILES)

    caption = (
        f"📖 <b>ختمة القرآن الكريم</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"📂 الملف: <b>{num}</b> من <b>{TOTAL_FILES}</b>\n"
        f"[{bar}] {pct}%\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🤲 اللهم اجعله في ميزان حسناتنا"
    )

    pdf_url = f"{RELEASE_BASE}/PdfQuran/{num}.pdf"
    mp3_url = f"{RELEASE_BASE_MP3}/Mp3Quran/{num}.mp3"

    print(f"📤 إرسال الملف رقم {num} ({pct}%)")
    send_document_url(pdf_url, caption)
    send_audio_url(mp3_url, f"🎵 استماع | الملف {num}")

    state["current_file"] = (n % TOTAL_FILES) + 1
    save_state(state)


def task_sabah():
    """6:00 ص — أذكار الصباح"""
    print("🌅 إرسال أذكار الصباح")
    send_photo_file(
        "Zeikr/sabah.jpg",
        "🌅 <b>أذكار الصباح</b>\nصباح الخير والبركات 🤍",
    )


def task_masa():
    """4:30 م — أذكار المساء"""
    print("🌆 إرسال أذكار المساء")
    send_photo_file(
        "Zeikr/masa.jpg",
        "🌆 <b>أذكار المساء</b>\nمساء النور والسعادة 🤍",
    )


def task_friday_kahf():
    """الجمعة 10:30 ص — سورة الكهف"""
    now = datetime.now(CAIRO_TZ)
    if now.weekday() != 4:
        print("⏭️ مش جمعة — تم التخطي")
        return
    print("📖 إرسال رسالة سورة الكهف")
    send_text(
        "📖 <b>لا تنس الكهف</b> 🌟\n\n"
        "https://www.slideshare.net/slideshow/ss-75952543/75952543\n\n"
        "تقبّل الله منا ومنكم ✨"
    )

# ─────────────────────────────────────────────
#  نقطة الدخول
# ─────────────────────────────────────────────
TASKS = {
    "daily_files" : task_daily_files,
    "sabah"       : task_sabah,
    "masa"        : task_masa,
    "kahf"        : task_friday_kahf,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        print(f"الاستخدام: python bot.py <{'|'.join(TASKS)}>")
        sys.exit(1)

    task_name = sys.argv[1]
    print(f"▶️  تشغيل المهمة: {task_name}")
    TASKS[task_name]()
    print("✅ انتهت المهمة بنجاح")
