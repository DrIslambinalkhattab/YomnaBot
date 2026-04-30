import os
import sys
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]        # -1001234567890
TOPIC_ID = os.environ["TOPIC_ID"]     # 33

ACTION = sys.argv[1] if len(sys.argv) > 1 else ""

BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

def send_photo(image_path, caption=""):
    with open(image_path, "rb") as photo:
        data = {
            "chat_id": CHAT_ID,
            "message_thread_id": TOPIC_ID,
            "caption": caption,
            "parse_mode": "HTML"
        }
        resp = requests.post(f"{BASE_URL}/sendPhoto", data=data, files={"photo": photo})
        print(f"send_photo [{image_path}]: {resp.status_code} {resp.text}")

def send_message(text):
    data = {
        "chat_id": CHAT_ID,
        "message_thread_id": TOPIC_ID,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    resp = requests.post(f"{BASE_URL}/sendMessage", data=data)
    print(f"send_message: {resp.status_code} {resp.text}")

if ACTION == "fajr":
    # أذكار الصباح - بعد الفجر
    send_photo("images/sabah.jpg", "🌅 <b>أذكار الصباح</b>\nاللهم بك أصبحنا وبك أمسينا، وبك نحيا وبك نموت وإليك النشور 🤍")

elif ACTION == "asr":
    # أذكار المساء - بعد العصر
    send_photo("images/masa.jpg", "🌇 <b>أذكار المساء</b>\nاللهم بك أمسينا وبك أصبحنا، وبك نحيا وبك نموت وإليك المصير 🤍")

elif ACTION == "night":
    # رسالة الليل - كل يوم
    send_message("🌙 <b>مساء النور والبركة</b>\n\nاللهم إني أمسيت أُشهدك وأُشهد حملة عرشك وملائكتك وجميع خلقك، أنك أنت الله لا إله إلا أنت وحدك لا شريك لك، وأن محمداً عبدك ورسولك 🤲")

elif ACTION == "friday":
    # يوم الجمعة - الساعة 8 صباحاً (إضافي فوق الروتين اليومي)
    friday_msg = (
        "✨ <b>جمعة مباركة</b> ✨\n\n"
        "قال رسول الله ﷺ:\n"
        "<i>«من قرأ سورة الكهف في يوم الجمعة، أضاء له من النور ما بين الجمعتين»</i>\n\n"
        "📖 اقرأ سورة الكهف:\n"
        "https://www.slideshare.net/slideshow/ss-75952543/75952543\n\n"
        "اللهم صلِّ وسلم على نبينا محمد 🤍"
    )
    send_message(friday_msg)

else:
    print(f"Unknown action: {ACTION}")
    sys.exit(1)
