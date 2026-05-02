"""
YomnaBot — يشتغل مرة واحدة عن طريق GitHub Actions
"""

import os
import json
import sys
import requests
from datetime import datetime
import pytz
import random

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
    """بيبعت الصوت كـ voice note عشان يشتغل مباشرة"""
    files = {"audio": (filename, data, "audio/mpeg")}
    r = requests.post(
        f"{BASE_URL}/sendAudio",
        data={**_base_params(), "caption": caption, "parse_mode": "HTML",
              "title": filename.replace(".mp3",""), "performer": "ختمة القرآن"},
        files=files,
    )
    print(f"🎵 Audio: {r.status_code} | {r.json().get('description','OK')}")

def download(url: str) -> bytes:
    print(f"⬇️  جاري التحميل: {url}")
    headers = {
        "Accept": "application/octet-stream",
        "User-Agent": "Mozilla/5.0",
    }
    r = requests.get(url, headers=headers, allow_redirects=True)
    print(f"   {'✅' if r.status_code==200 else '❌'} {len(r.content)//1024} KB | {r.status_code}")
    return r.content

# ─────────────────────────────────────────────
#  Progress bar
# ─────────────────────────────────────────────
def progress_bar(current: int, total: int) -> str:
    length  = 12
    filled  = int((current / total) * length)
    empty   = length - filled
    pct     = round((current / total) * 100, 1)
    bar     = "█" * filled + "░" * empty
    remaining = total - current

    # نجوم التقدم
    if pct < 25:   stars = "⭐"
    elif pct < 50: stars = "⭐⭐"
    elif pct < 75: stars = "⭐⭐⭐"
    else:          stars = "⭐⭐⭐⭐"

    return (
        f"<code>|{bar}|</code>  <b>{pct}%</b>  {stars}\n"
        f"📂 <b>{current}</b> من <b>{total}</b>  •  ⏳ باقي <b>{remaining}</b>"
    )

# ─────────────────────────────────────────────
#  رسائل التحفيز حسب التقدم
# ─────────────────────────────────────────────
def motivational(pct: float) -> str:
    if pct < 10:
        msgs = [
            "🌱 <i>كل رحلة تبدأ بخطوة — بارك الله في بدايتكم</i>",
            "🌱 <i>البداية نور، والنور يكبر مع كل يوم</i>",
        ]
    elif pct < 25:
        msgs = [
            "🌿 <i>ماشيين بثبات — والثبات أعظم من العجلة</i>",
            "🌿 <i>خير العمل ما داوم عليه صاحبه وإن قلّ</i>",
        ]
    elif pct < 50:
        msgs = [
            "🌸 <i>ربع الطريق خلفنا — اللهم أعنّا على إتمامه</i>",
            "🌸 <i>كل يوم خطوة — وكل خطوة في ميزان حسناتكم</i>",
        ]
    elif pct < 75:
        msgs = [
            "🌺 <i>أكثر من النصف — وما أجمل أن يُتم المؤمن ما بدأ</i>",
            "🌺 <i>في منتصف الطريق والهمم عالية — بارك الله فيكم</i>",
        ]
    elif pct < 90:
        msgs = [
            "🌟 <i>قاربنا الختم — اللهم بلّغنا وتقبّل منا</i>",
            "🌟 <i>الخواتيم بيد الله — اللهم اجعل خواتيمنا خيراً</i>",
        ]
    else:
        msgs = [
            "✨ <i>على وشك الختمة — اللهم تقبّل منا ومنكم</i>",
            "✨ <i>لحظات وتكتمل الختمة — فلا تفوّتوا هذا الشرف</i>",
        ]
    return random.choice(msgs)

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
        f"━━━━━━━━━━━━━━━━\n"
        f"🗓 <i>{date_str}</i>   •   📂 الجزء <b>{num}</b>\n\n"
        f"{bar}\n\n"
        f"{motiv}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🤲 <i>اللهم اجعله في ميزان حسناتنا جميعاً</i>"
    )

    caption_mp3 = (
        f"🎧 <b>تلاوة الجزء {num}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>«وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا»</i>\n"
        f"<i>استمع وقلبك حاضر — الأجر مضاعف</i>"
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

    # رسالة نصية تمهيدية
    send_text(
        "🌅 <b>أذكار الصباح</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "<i>«أَصْبَحْنَا وَأَصْبَحَ الْمُلْكُ لِلَّهِ»</i>\n\n"
        "🤍 <b>ابدأ يومك بذكر الله</b>\n"
        "<i>من حافظ على أذكار الصباح كان في حِفظ الله طوال يومه</i>"
    )

    # ملف الأذكار PDF
    azkar_url = f"{RELEASE_BASE}/al-azkar.pdf"
    caption = (
        f"📋 <b>أذكار الصباح</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>اقرأها بتأمل — كل ذكر له أثر</i>"
    )
    send_document_bytes(download(azkar_url), "al-azkar.pdf", caption)


# ─────────────────────────────────────────────
#  المهمة الثانية ب: أذكار المساء
# ─────────────────────────────────────────────
def task_masa():
    print("🌆 إرسال أذكار المساء")

    send_text(
        "🌆 <b>أذكار المساء</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "<i>«أَمْسَيْنَا وَأَمْسَى الْمُلْكُ لِلَّهِ»</i>\n\n"
        "🤍 <b>اختم نهارك بذكر الله</b>\n"
        "<i>من حافظ على أذكار المساء كان في حِفظ الله طوال ليله</i>"
    )

    azkar_url = f"{RELEASE_BASE}/al-azkar.pdf"
    caption = (
        f"📋 <b>أذكار المساء</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>اقرأها بتأمل — كل ذكر له أثر</i>"
    )
    send_document_bytes(download(azkar_url), "al-azkar.pdf", caption)


# ─────────────────────────────────────────────
#  المهمة الثالثة: الجمعة — سورة الكهف
# ─────────────────────────────────────────────
def task_friday_kahf():
    print("📖 إرسال سورة الكهف")

    send_text(
        "🕌 <b>جمعة مباركة</b>\n"
        "━━━━━━━━━━━━━━━━\n\n"
        "📖 <b>لا تنسَ سورة الكهف اليوم</b>\n\n"
        "<i>«مَنْ قَرَأَ سُورَةَ الْكَهْفِ فِي يَوْمِ الْجُمُعَةِ</i>\n"
        "<i>أَضَاءَ لَهُ مِنَ النُّورِ مَا بَيْنَ الْجُمُعَتَيْنِ»</i>\n\n"
        "━━━━━━━━━━━━━━━━\n"
        "🤲 <i>تقبّل الله منا ومنكم صالح الأعمال</i>"
    )

    caption_pdf = (
        f"📗 <b>سورة الكهف</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>اقرأ واحتسب — النور ينتظرك</i>"
    )
    caption_mp3 = (
        f"🎧 <b>تلاوة سورة الكهف</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"<i>«وَرَتِّلِ الْقُرْآنَ تَرْتِيلًا»</i>"
    )

    pdf_url = f"{RELEASE_KAHF}/al-kahf.pdf"
    mp3_url = f"{RELEASE_KAHF}/al-kahf.mp3"

    send_document_bytes(download(pdf_url), "al-kahf.pdf", caption_pdf)
    send_audio_bytes(download(mp3_url), "al-kahf.mp3", caption_mp3)


# ─────────────────────────────────────────────
#  التذكيرات اليومية
# ─────────────────────────────────────────────
def task_remind_morning():
    """10 ص — تذكير بداية النهار"""
    msgs = [
        (
            "☀️ <b>تذكير الضحى</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "📌 <b>مع التذكير بمهام اليوم:</b>\n\n"
            "📖 ورد القرآن اليومي — <i>هل قرأت جزءك؟</i>\n"
            "🤲 أذكار الصباح — <i>هل حصّنت نفسك؟</i>\n"
            "📿 الأذكار المطلقة — <i>سبّح واستغفر في أي وقت</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "<i>«وَمَن يَتَّقِ اللَّهَ يَجْعَل لَّهُ مَخْرَجًا»</i>"
        ),
        (
            "☀️ <b>صباح الخير والبركة</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "⏰ النهار في أوله والفرص متاحة!\n\n"
            "📖 <i>ورد القرآن ينتظرك</i>\n"
            "🌿 <i>الأذكار تُحصّن يومك</i>\n"
            "💡 <i>دقائق مع الله تُصلح بقية يومك كله</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "🤲 <i>اللهم أعنّا على ذكرك وشكرك وحسن عبادتك</i>"
        ),
    ]
    send_text(random.choice(msgs))


def task_remind_midday():
    """2 ظ — تذكير منتصف النهار"""
    msgs = [
        (
            "🌤 <b>وقفة منتصف النهار</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "النهار مضى نصفه — كيف حالك مع الله؟\n\n"
            "📖 <i>لو ما قرأتش ورد القرآن — دلوقتي وقته</i>\n"
            "🤲 <i>لو نسيت الأذكار — الله غفور رحيم، ابدأ من جديد</i>\n"
            "📿 <i>سبحان الله وبحمده — مائة مرة تمحو الخطايا</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "<i>«أَلَا بِذِكْرِ اللَّهِ تَطْمَئِنُّ الْقُلُوبُ»</i>"
        ),
        (
            "🌤 <b>لحظة وسط الزحمة</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "وسط مشاغل الدنيا — لا تنس نصيبك من الله 🤍\n\n"
            "💬 قل: <b>سبحان الله وبحمده سبحان الله العظيم</b>\n"
            "<i>كلمتان خفيفتان على اللسان</i>\n"
            "<i>ثقيلتان في الميزان</i>\n"
            "<i>حبيبتان إلى الرحمن</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "📖 <i>ورد القرآن لسه بينتظرك لو ما كملتش</i>"
        ),
    ]
    send_text(random.choice(msgs))


def task_remind_night():
    """9 م — تذكير آخر النهار"""
    msgs = [
        (
            "🌙 <b>محطة آخر النهار</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "قبل ما ينتهي يومك — حاسب نفسك بهدوء:\n\n"
            "✅ <i>هل قرأت وردك اليوم؟</i>\n"
            "✅ <i>هل قلت أذكار الصباح والمساء؟</i>\n"
            "✅ <i>هل ذكرت الله في غيرها؟</i>\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "🌙 <b>أذكار النوم — لا تنم بدونها</b>\n"
            "<i>آية الكرسي • الإخلاص • المعوذتان</i>\n"
            "<i>«اللهم باسمك أموت وأحيا»</i>\n\n"
            "🤲 <i>اللهم اجعل آخر كلامنا لا إله إلا الله</i>"
        ),
        (
            "🌙 <b>الليل على الأبواب</b>\n"
            "━━━━━━━━━━━━━━━━\n\n"
            "المداومة هي السر 🌟\n\n"
            "<i>«إن أحب الأعمال إلى الله</i>\n"
            "<i>أدومها وإن قلّ»</i>\n\n"
            "كل يوم بتلتزم فيه — هو انتصار 🏆\n"
            "وكل تقصير — فرصة للتوبة والبداية من جديد\n\n"
            "━━━━━━━━━━━━━━━━\n"
            "💤 <i>نامي على ذكر الله</i>\n"
            "🤲 <i>اللهم تقبّل منا ومنكم</i>"
        ),
    ]
    send_text(random.choice(msgs))


# ─────────────────────────────────────────────
#  نقطة الدخول
# ─────────────────────────────────────────────
TASKS = {
    "daily_files"    : task_daily_files,
    "sabah"          : task_sabah,
    "masa"           : task_masa,
    "kahf"           : task_friday_kahf,
    "remind_morning" : task_remind_morning,
    "remind_midday"  : task_remind_midday,
    "remind_night"   : task_remind_night,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        print(f"الاستخدام: python bot.py <{'|'.join(TASKS)}>")
        sys.exit(1)

    task_name = sys.argv[1]
    print(f"▶️  تشغيل المهمة: {task_name}")
    TASKS[task_name]()
    print("✅ انتهت المهمة بنجاح")
