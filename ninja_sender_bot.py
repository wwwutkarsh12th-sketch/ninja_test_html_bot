import telebot
import time

API_TOKEN = "8245590704:AAFKoZ45su_yZ_V89zI5vU1pHC54XgUNdP8"
bot = telebot.TeleBot(API_TOKEN)

MY_USER_ID = 1751485507
TARGET_CHATS = [
    "-1002608856903",   # Ninja Study Channel 1
    "-1003009883999",   # Ninja_Study Channel 2
    "-1002798379392",   # Ninja study Channel 3
    "-1002515443540",   # Ninja study Channel 4
    "-1001970563628",   # Utkarsh rpse 2nd grade
    "-1002961757635",   # 2nd Grade 2nd Paper(Science) Online Course(Recorded From Jaipur Classroom)
    "-1003059468901",   # RPSC 2nd Grade 2nd Paper(Maths) Batch(Recorded From Jodhpur Classroom)
]


def safe_copy_message(chat_id, from_chat, message_id):
    """Copy message with auto-retry if FloodWait occurs"""
    while True:
        try:
            bot.copy_message(chat_id, from_chat, message_id)
            break  # success -> loop se bahar
        except Exception as e:
            err = str(e)
            if "Flood control exceeded" in err or "Too Many Requests" in err:
                # Telegram ne force wait lagaya hai
                wait_time = 5
                for s in err.split():
                    if s.isdigit():
                        wait_time = int(s) + 1
                        break
                print(f"⏳ FloodWait: waiting {wait_time} sec before retry...")
                time.sleep(wait_time)
            else:
                print(f"❌ Error sending to {chat_id}: {e}")
                break


@bot.message_handler(func=lambda message: True,
                     content_types=['text', 'photo', 'video', 'document', 'audio', 'sticker', 'voice', 'animation'])
def forward_personal(message):
    if message.from_user.id == MY_USER_ID:   # ✅ sirf aapke messages
        for chat_id in TARGET_CHATS:
            safe_copy_message(chat_id, message.chat.id, message.message_id)


print("🚀 Bot is running...")
bot.polling(none_stop=True, interval=0, timeout=20)
