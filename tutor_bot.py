import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ================================
#  CONFIG
# ================================
BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
TUTORS_GROUP_ID = -1003374172310   # Sening guruhing

logging.basicConfig(level=logging.INFO)

# ==================================
# 4 TA TIL PAKETI
# ==================================
LANG = {
    "uz": {
        "start": "Assalomu alaykum! Tilni tanlang:",
        "share": "📱 Iltimos, telefon raqamingizni ulashing:",
        "faculty": "🏫 Fakultetingizni tanlang:",
        "tutor": "👨‍🏫 Tyutoringizni tanlang:",
        "write": "Savolingizni yozib yuboring:",
        "sent": "✔ Savolingiz tyutorga yuborildi! Tez orada javob olasiz.",
        "thanks": "Rahmat! Murojaatingiz qabul qilindi.",
    },
    "ru": {
        "start": "Здравствуйте! Выберите язык:",
        "share": "📱 Пожалуйста, отправьте свой номер телефона:",
        "faculty": "🏫 Выберите факультет:",
        "tutor": "👨‍🏫 Выберите тьютора:",
        "write": "Введите свой вопрос:",
        "sent": "✔ Ваш вопрос отправлен! Ожидайте ответ.",
        "thanks": "Спасибо! Ваш запрос принят.",
    },
    "en": {
        "start": "Hello! Choose language:",
        "share": "📱 Please share your phone number:",
        "faculty": "🏫 Select your faculty:",
        "tutor": "👨‍🏫 Select your tutor:",
        "write": "Write your question:",
        "sent": "✔ Your question was sent! You’ll get an answer soon.",
        "thanks": "Thanks! Your request has been received.",
    },
    "tm": {
        "start": "Salam! Dili saýlaň:",
        "share": "📱 Telefon belgiňiz paýlaşyň:",
        "faculty": "🏫 Fakulteti saýlaň:",
        "tutor": "👨‍🏫 Tyutory saýlaň:",
        "write": "Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy! Jogap tiz gelýär.",
        "thanks": "Sag boluň! Siziň müraciýetiňiz kabul edildi.",
    }
}

# ==================================
# FAKULTETLAR & TYUTORLAR
# ==================================
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [
            {"name": "Xursandova Dilafruz", "id": 1720369159}
        ]
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "ru": "Экология и право",
        "en": "Ecology and Law",
        "tm": "Ekologiýa we hukuk",
        "tutors": [
            {"name": "Ahmedova Iroda", "id": 6926132637},
            {"name": "Shonazarov Akbar", "id": 2052678760},
            {"name": "Saidova Xursanoy", "id": 702931087},
            {"name": "Hudo Nazarova Dilnavoz", "id": 310033808},
        ]
    },
    "mech": {
        "uz": "Mexanizatsiya",
        "ru": "Механизация сельского хозяйства",
        "en": "Mechanization",
        "tm": "Mehanizasiýa",
        "tutors": []
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tm": "Energetika",
        "tutors": [
            {"name": "Botir Abdullaev", "id": 485351327}
        ]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources & Cadastre",
        "tm": "Ýer serişdeleri we kadastr",
        "tutors": [
            {"name": "Turgunova Maftuna", "id": 8376601534},
            {"name": "Abdullayeva Oliya", "id": 2134838705},
        ]
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tm": "Gidromeliorasiýa",
        "tutors": [
            {"name": "Ahmedjanova Gulchehra", "id": 503802473}
        ]
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"name": "Egamova Dilbar", "id": 115619153},
            {"name": "Shodiyeva Gulbahor", "id": 401016810},
        ]
    }
}

# Savolni saqlash
pending = {}   # user_id → {"tutor_id":..., "faculty":..., "question":...}


# ================================
# /start
# ================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]

    await update.message.reply_text(
        "Assalomu alaykum! Tilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================================
# TIL TANLASH
# ================================
async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )

    await q.edit_message_text(LANG[lang]["share"])
    await q.message.reply_text(LANG[lang]["share"], reply_markup=kb)


# ================================
# TELEFON QABUL QILINGANDA
# ================================
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["phone"] = update.message.contact.phone_number
    lang = context.user_data["lang"]

    # Fakultetlar menyusi
    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG[lang]["faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================================
# FAKULTET TANLANGANDA
# ================================
async def choose_fac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    fac_key = q.data.split("|")[1]
    context.user_data["faculty_key"] = fac_key
    lang = context.user_data["lang"]

    tutors = FACULTIES[fac_key]["tutors"]

    # Tyutorlar yo‘q bo‘lsa to‘g‘ri savolga o‘tadi
    if not tutors:
        await q.edit_message_text(LANG[lang]["write"])
        return

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{fac_key}|{t['id']}")]
        for t in tutors
    ]

    await q.edit_message_text(
        LANG[lang]["tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ================================
# TUTOR TANLANGANDA
# ================================
async def choose_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    _, facet, tutor_id = q.data.split("|")
    tutor_id = int(tutor_id)

    context.user_data["tutor_id"] = tutor_id
    context.user_data["faculty_key"] = facet

    lang = context.user_data["lang"]

    await q.edit_message_text(LANG[lang]["write"])


# ================================
# TALABANING SAVOLINI QABUL QILISH
# ================================
async def student_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    lang = context.user_data["lang"]

    question = update.message.text
    phone = context.user_data["phone"]
    tutor_id = context.user_data.get("tutor_id")
    fac_key = context.user_data["faculty_key"]

    faculty_name = FACULTIES[fac_key][lang]

    # Saqlash
    pending[user.id] = {
        "tutor_id": tutor_id,
        "faculty": faculty_name,
        "question": question
    }

    # Guruhga yuborish
    txt = (
        f"📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 +{phone}\n"
        f"🏫 Fakultet: {faculty_name}\n"
        f"👨‍🏫 Tyutor: [⤵️](tg://user?id={tutor_id})\n\n"
        f"💬 *Savol:* {question}"
    )

    await context.bot.send_message(
        TUTORS_GROUP_ID,
        txt,
        parse_mode="Markdown"
    )

    await update.message.reply_text(LANG[lang]["sent"])


# ================================
# TYUTOR JAVOB BERSA → TALABAGA BORADI
# ================================
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutor = update.message.from_user

    for user_id, data in pending.items():
        if data["tutor_id"] == tutor.id:
            await context.bot.send_message(
                user_id,
                f"📨 *Tyutordan javob:*\n{update.message.text}",
                parse_mode="Markdown"
            )
            return


# ================================
# MAIN
# ================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_lang, pattern="^lang\\|"))
    app.add_handler(CallbackQueryHandler(choose_fac, pattern="^faculty\\|"))
    app.add_handler(CallbackQueryHandler(choose_tutor, pattern="^tutor\\|"))

    app.add_handler(MessageHandler(filters.CONTACT, get_phone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, student_question))
    app.add_handler(MessageHandler(filters.REPLY, tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
