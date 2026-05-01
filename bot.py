"""
YomnaBot — يشتغل مرة واحدة عن طريق GitHub Actions
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
BOT_TOKEN        = os.environ["BOT_TOKEN"]
CHAT_ID          = os.environ.get("CHAT_ID", "-1003844022713")
TOPIC_ID         = os.environ.get("TOPIC_ID", "33")
RELEASE_BASE     = os.environ.get("RELEASE_BASE", "")      # v1.1 — PDF
RELEASE_BASE_MP3 = os.environ.get("RELEASE_BASE_MP3", "")  # v1.0 — MP3
RELEASE_KAHF     = os.environ.get("RELEASE_KAHF", "")      # v1.2 — الكهف
CAIRO_TZ         = pytz.timezone("Africa/Cairo")
TOTAL_FILES      = 604
STATE_FILE       = "state.json"
BASE_URL         = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
    print(f"📨 نص: {r.status_code}")

def send_document_bytes(data: bytes, filename: str, caption: str = ""):
    files = {"document": (filename, data, "application/pdf")}
    r = requests.post(
        f"{BASE_URL}/sendDocument",
        data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
        files=files,
    )
    print(f"📄 PDF: {r.status_code} | {r.json().get('description','OK')}")

def send_audio_bytes(data: bytes, filename: str, caption: str = ""):
    # نبعته كـ document عشان تيليغرام يتعامل معاه صح
    files = {"document": (filename, data, "audio/mpeg")}
    r = requests.post(
        f"{BASE_URL}/sendDocument",
        data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
        files=files,
    )
    print(f"🎵 MP3: {r.status_code} | {r.json().get('description','OK')}")

def send_photo_file(path: str, caption: str = ""):
    with open(path, "rb") as photo:
        r = requests.post(
            f"{BASE_URL}/sendPhoto",
            data={**_base_params(), "caption": caption, "parse_mode": "HTML"},
            files={"photo": photo},
        )
    print(f"🖼️ صورة: {r.status_code}")

def download(url: str) -> bytes:
    print(f"⬇️  جاري التحميل: {url}")
    headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.get(url, headers=headers, allow_redirects=True)
    print(f"   ✅ {len(r.content) // 1024} KB | status: {r.status_code} | type: {r.headers.get('content-type','?')}")
    return r.content

# ─────────────────────────────────────────────
#  Progress bar — مزخرف
# ─────────────────────────────────────────────
def progress_bar(current: int, total: int) -> str:
    length   = 10
    filled   = int((current / total) * length)
    empty    = length - filled
    pct      = round((current / total) * 100, 1)

    # اخترنا رموز تليق بالمقام
    bar = "🟩" * filled + "⬜" * empty

    remaining = total - current
    return (
        f"<b>[{bar}]</b>  <b>{pct}%</b>\n"
        f"📂 الملف: <b>{current}</b> من <b>{total}</b>  |  "
        f"⏳ متبقي: <b>{remaining}</b> ملف"
    )

# ─────────────────────────────────────────────
#  رسائل التحفيز حسب التقدم
# ─────────────────────────────────────────────
def motivational(pct: float) -> str:
    if pct < 10:
        return "🌱 <i>البداية نور — بارك الله في خطواتكم</i>"
    elif pct < 25:
        return "🌿 <i>ماشيين بثبات — الله يكتب لكم الأجر</i>"
    elif pct < 50:
        return "🌸 <i>في منتصف الطريق — ولا تهنوا ولا تحزنوا</i>"
    elif pct < 75:
        return "🌺 <i>أكثر من النص — الله يتمم علينا بخير</i>"
    elif pct < 90:
        return "🌟 <i>قاربنا — اللهم بلّغنا الختم</i>"
    else:
        return "✨ <i>على وشك الختمة — اللهم تقبّل منا ومنكم</i>"

# ─────────────────────────────────────────────
#  المهمة الأولى: PDF + MP3 كل يوم 5:30 ص
# ─────────────────────────────────────────────
def task_daily_files():
    state = load_state()
    n     = state["current_file"]
    num   = f"{n:03d}"
    pct   = round((n / TOTAL_FILES) * 100, 1)
    bar   = progress_bar(n, TOTAL_FILES)
    motiv = motivational(pct)

    now_cairo = datetime.now(CAIRO_TZ)
    date_str  = now_cairo.strftime("%d / %m / %Y")

    caption_pdf = (
        f"📖 <b>ختمة القرآن الكريم</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"🗓 <i>{date_str}</i>\n\n"
        f"{bar}\n\n"
        f"{motiv}\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"🤲 <i>اللهم اجعله في ميزان حسناتنا</i>"
    )

    caption_mp3 = (
        f"🎧 <b>استماع | الجزء {num}</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>«وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا»</i>"
    )

    pdf_url = f"{RELEASE_BASE}/{num}.pdf"
    mp3_url = f"{RELEASE_BASE_MP3}/{num}.mp3"

    print(f"📤 إرسال الملف رقم {num} ({pct}%)")
    send_document_bytes(download(pdf_url), f"{num}.pdf", caption_pdf)
    send_audio_bytes(download(mp3_url), f"{num}.mp3", caption_mp3)

    state["current_file"] = (n % TOTAL_FILES) + 1
    save_state(state)


# ─────────────────────────────────────────────
#  المهمة الثانية أ: أذكار الصباح
# ─────────────────────────────────────────────
def task_sabah():
    print("🌅 إرسال أذكار الصباح")
    caption = (
        f"🌅 <b>أذكار الصباح</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>«يُسَبِّحُ لِلَّهِ مَا فِي السَّمَاوَاتِ وَمَا فِي الْأَرْضِ»</i>\n\n"
        f"🤍 <b>أحسن ما تبدأ به يومك</b>\n"
        f"<i>حافظ عليها تُكتب من الذاكرين</i>"
    )
    send_photo_file("Zeikr/sabah.jpg", caption)


# ─────────────────────────────────────────────
#  المهمة الثانية ب: أذكار المساء
# ─────────────────────────────────────────────
def task_masa():
    print("🌆 إرسال أذكار المساء")
    caption = (
        f"🌆 <b>أذكار المساء</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>«وَسَبِّحْ بِحَمْدِ رَبِّكَ قَبْلَ غُرُوبِ الشَّمْسِ»</i>\n\n"
        f"🤍 <b>اختم يومك بذكر الله</b>\n"
        f"<i>حافظ عليها تُكتب من الذاكرين</i>"
    )
    send_photo_file("Zeikr/masa.jpg", caption)


# ─────────────────────────────────────────────
#  المهمة الثالثة: الجمعة — سورة الكهف
# ─────────────────────────────────────────────
def task_friday_kahf():
    print("📖 إرسال سورة الكهف")

    # رسالة تمهيدية أولاً
    intro = (
        f"🕌 <b>يوم الجمعة المبارك</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n\n"
        f"📖 <b>لا تنسَ سورة الكهف</b>\n\n"
        f"<i>«مَنْ قَرَأَ سُورَةَ الْكَهْفِ فِي يَوْمِ الْجُمُعَةِ،</i>\n"
        f"<i>أَضَاءَ لَهُ مِنَ النُّورِ مَا بَيْنَ الْجُمُعَتَيْنِ»</i>\n\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"🤲 <i>تقبّل الله منا ومنكم</i> ✨"
    )
    send_text(intro)

    # PDF سورة الكهف
    caption_pdf = (
        f"📗 <b>سورة الكهف</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>اقرأ واحتسب الأجر عند الله</i>"
    )

    # MP3 سورة الكهف
    caption_mp3 = (
        f"🎧 <b>استماع | سورة الكهف</b>\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"<i>«وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا»</i>"
    )

    pdf_url = f"{RELEASE_KAHF}/Al-Kahf.pdf"
    mp3_url = f"{RELEASE_KAHF}/Al-Kahf.mp3"

    send_document_bytes(download(pdf_url), "al-kahf.pdf", caption_pdf)
    send_audio_bytes(download(mp3_url), "al-kahf.mp3", caption_mp3)


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
