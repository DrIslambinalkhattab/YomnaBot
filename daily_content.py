"""
daily_content.py — آية اليوم وحديث اليوم
يشتغل كل يوم الساعة 8 ص بتوقيت القاهرة
"""

import os
import sys
import requests
from datetime import datetime
import pytz

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID   = os.environ.get("CHAT_ID", "-1003844022713")
TOPIC_ID  = os.environ.get("TOPIC_ID", "33")
CAIRO_TZ  = pytz.timezone("Africa/Cairo")
BASE_URL  = f"https://api.telegram.org/bot{BOT_TOKEN}"

def _base_params():
    return {"chat_id": CHAT_ID, "message_thread_id": TOPIC_ID}

def send_text(text: str):
    r = requests.post(
        f"{BASE_URL}/sendMessage",
        data={**_base_params(), "text": text, "parse_mode": "HTML"},
    )
    print(f"📨 {r.status_code}")

# ─────────────────────────────────────────────
#  آية اليوم
# ─────────────────────────────────────────────
def get_ayah() -> dict | None:
    now = datetime.now(CAIRO_TZ)
    # نختار آية حسب اليوم في السنة (1-365) من أصل 6236 آية
    day_of_year = now.timetuple().tm_yday
    ayah_number = ((day_of_year - 1) % 6236) + 1

    try:
        r = requests.get(
            f"https://api.alquran.cloud/v1/ayah/{ayah_number}/ar.alafasy",
            timeout=10
        )
        data = r.json()
        if data["status"] == "OK":
            ayah = data["data"]
            # جيب التفسير
            r2 = requests.get(
                f"https://api.alquran.cloud/v1/ayah/{ayah_number}/ar.muyassar",
                timeout=10
            )
            tafseer = r2.json()["data"]["text"] if r2.json()["status"] == "OK" else ""
            return {
                "text"    : ayah["text"],
                "surah"   : ayah["surah"]["name"],
                "ayah_num": ayah["numberInSurah"],
                "tafseer" : tafseer,
            }
    except Exception as e:
        print(f"❌ خطأ في API الآية: {e}")
    return None

def task_ayah():
    print("📖 إرسال آية اليوم")
    ayah = get_ayah()
    if not ayah:
        send_text("📖 <b>آية اليوم</b>\n\n<i>تعذّر تحميل الآية — جرب لاحقاً</i>")
        return

    msg = (
        f"📖 <b>آية اليوم</b>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"❝ <b>{ayah['text']}</b> ❞\n\n"
        f"📌 <i>سورة {ayah['surah']} — الآية {ayah['ayah_num']}</i>\n\n"
        f"┄┄┄┄┄┄┄┄┄┄┄┄\n"
        f"💡 <b>المعنى:</b>\n"
        f"<i>{ayah['tafseer']}</i>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🤲 <i>تدبّر — فالقرآن شفاء لما في الصدور</i>"
    )
    send_text(msg)

# ─────────────────────────────────────────────
#  حديث اليوم
# ─────────────────────────────────────────────
def get_hadith() -> dict | None:
    now = datetime.now(CAIRO_TZ)
    day_of_year = now.timetuple().tm_yday

    # كتب الحديث المتاحة — صحيح البخاري (7563 حديث) وصحيح مسلم (3033)
    books = [
        {"id": "bukhari", "name": "صحيح البخاري", "total": 7563},
        {"id": "muslim",  "name": "صحيح مسلم",   "total": 3033},
    ]
    book   = books[day_of_year % 2]
    hadith_num = ((day_of_year - 1) % book["total"]) + 1

    try:
        r = requests.get(
            f"https://api.hadith.gading.dev/books/{book['id']}/{hadith_num}",
            timeout=10
        )
        data = r.json()
        if data["error"] == False:
            return {
                "text": data["data"]["contents"]["ar"],
                "book": book["name"],
                "num" : hadith_num,
            }
    except Exception as e:
        print(f"❌ خطأ في API الحديث: {e}")
    return None

def task_hadith():
    print("📜 إرسال حديث اليوم")
    hadith = get_hadith()
    if not hadith:
        send_text("📜 <b>حديث اليوم</b>\n\n<i>تعذّر تحميل الحديث — جرب لاحقاً</i>")
        return

    msg = (
        f"📜 <b>حديث اليوم</b>\n"
        f"━━━━━━━━━━━━━━━━\n\n"
        f"❝ <b>{hadith['text']}</b> ❞\n\n"
        f"📌 <i>{hadith['book']} — حديث رقم {hadith['num']}</i>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🌿 <i>اقرأه بتمعّن — ففيه هدى ونور</i>"
    )
    send_text(msg)

# ─────────────────────────────────────────────
#  نقطة الدخول
# ─────────────────────────────────────────────
TASKS = {
    "ayah"  : task_ayah,
    "hadith": task_hadith,
}

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in TASKS:
        print(f"الاستخدام: python daily_content.py <{'|'.join(TASKS)}>")
        sys.exit(1)
    task = sys.argv[1]
    print(f"▶️  {task}")
    TASKS[task]()
    print("✅ انتهت المهمة")
