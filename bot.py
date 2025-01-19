import telebot
from telebot import types
from rembg import remove
from PIL import Image
import io
import os

# ضع التوكن الخاص بالبوت هنا
API_TOKEN = "7584543289:AAFxr120qKmj1BEDPt5aKwPvX0HrtF8iY5E"

# تهيئة البوت
bot = telebot.TeleBot(API_TOKEN)

# مجلد لحفظ الصور المؤقتة
if not os.path.exists("temp"):
    os.makedirs("temp")


# أمر /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "مرحبًا بك! أرسل لي صورة وسأقوم بقص الخلفية أو تحسين الصورة.")


# التعامل مع الصور المرسلة
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    # تحميل الصورة من الرسالة
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)

    # حفظ الصورة في ملف مؤقت
    input_path = f"temp/{message.photo[-1].file_id}.jpg"
    with open(input_path, 'wb') as file:
        file.write(downloaded_file)

    # إرسال خيارات للمستخدم
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🖼️ قص الخلفية", callback_data=f"remove_bg:{input_path}"),
        types.InlineKeyboardButton("✨ تحسين الصورة", callback_data=f"enhance_img:{input_path}")
    )
    bot.reply_to(message, "ماذا تريد أن أفعل بالصورة؟", reply_markup=markup)


# التعامل مع الاختيارات
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    if call.data.startswith("remove_bg:"):
        input_path = call.data.split(":")[1]
        output_path = input_path.replace(".jpg", "_no_bg.png")

        try:
            # إزالة الخلفية
            with open(input_path, 'rb') as file:
                input_image = file.read()
            output_image = remove(input_image)

            # حفظ الصورة الجديدة
            with open(output_path, 'wb') as file:
                file.write(output_image)

            # إرسال الصورة للمستخدم
            with open(output_path, 'rb') as file:
                bot.send_photo(call.message.chat.id, file, caption="تمت إزالة الخلفية بنجاح!")

        except Exception as e:
            bot.reply_to(call.message, f"حدث خطأ أثناء معالجة الصورة: {e}")

    elif call.data.startswith("enhance_img:"):
        input_path = call.data.split(":")[1]
        output_path = input_path.replace(".jpg", "_enhanced.jpg")

        try:
            # تحسين الصورة باستخدام PIL
            img = Image.open(input_path)
            enhanced_img = img.resize((img.width * 2, img.height * 2))  # تكبير الصورة
            enhanced_img.save(output_path)

            # إرسال الصورة المحسنة
            with open(output_path, 'rb') as file:
                bot.send_photo(call.message.chat.id, file, caption="تم تحسين الصورة بنجاح!")

        except Exception as e:
            bot.reply_to(call.message, f"حدث خطأ أثناء تحسين الصورة: {e}")

    # حذف الملفات المؤقتة
    try:
        os.remove(input_path)
        if os.path.exists(output_path):
            os.remove(output_path)
    except Exception as e:
        print(f"Error deleting files: {e}")


# بدء تشغيل البوت
print("Bot is running...")
bot.polling()