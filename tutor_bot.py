import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
TUTORS_GROUP_ID = -1003374172310   # Sening guruhing

# =======================================
# 4 TIL PAKETI
# =======================================
LANG = {
    "uz": {
        "start": "Assalomu alaykum! Tilni tanlang:",
        "share": "📱 Iltimos, telefon raqamingizni ulashing:",
        "faculty": "🏫 Fakultetingizni tanlang:",
        "tutor": "👨‍🏫 Tyutoringizni tanlang:",
        "write": "Savolingizni yozing:",
        "sent": "✔ Savolingiz tyutorga yuborildi!",
        "done": "Rahmat! Tez orada sizga javob beriladi."
    },
    "ru": {
        "start": "Здравствуйте! Выберите язык:",
        "share": "📱 Пожалуйста, отправьте свой номер:",
        "faculty": "🏫 Выберите факультет:",
        "tutor": "👨‍🏫 Выберите тьютора:",
        "write": "Введите ваш вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьютору!",
        "done": "Спасибо! Ожидайте ответ."
    },
    "en": {
        "start": "Hello! Choose language:",
        "share": "📱 Please share your phone number:",
        "faculty": "🏫 Select your faculty:",
        "tutor": "👨‍🏫 Select your tutor:",
        "write": "Write your question:",
        "sent": "✔ Your question was sent!",
        "done": "Thank you! You will get a reply soon."
    },
    "tm": {
        "start": "Salam! Dili saýlaň:",
        "share": "📱 Telefon belgiňiz paýlaşyň:",
        "faculty": "🏫 Fakulteti saýlaň:",
        "tutor": "👨‍🏫 Tyutory saýlaň:",
        "write": "Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy!",
        "done": "Sag boluň! Jogap tiz gelýär."
    }
}

# =======================================
# FAKULTETLAR VA TYUTORLAR
# =======================================
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
        "en": "Land & Cadastre",
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


# Talabaning savoli saqlanadi
pending = {}   # user_id → tutor_id


# ===============================
# /start
# ===============================
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


# ===============================
# Til tanlash
# ===============================
async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang

    # Raqamni bir marta so‘rash
    button = InlineKeyboardButton("📱 Raqamni ulashish", callback_data="share")
    markup = InlineKeyboardMarkup([[button]])

    await q.edit_message_text(LANG[lang]["share"], reply_markup=markup)


# ===============================
# Raqam ulashish tugmasi
# ===============================
async def request_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = context.user_data["lang"]

    # Telefon so‘rash
    await q.message.reply_contact(
        phone_number="123",
        first_name="Telefon raqamni shu yerdan ulashing"
    )


# ===============================
# Kontakt kelganda
# ===============================
async def got_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone

    lang = context.user_data["lang"]

    # Fakultet tugmalari
    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG[lang]["faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===============================
# Fakultet tanlash
# ===============================
async def choose_fac(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = context.user_data["lang"]

    fac_key = q.data.split("|")[1]
    context.user_data["facet"] = fac_key

    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        await q.edit_message_text(LANG[lang]["write"])
        return

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{t['id']}")]
        for t in tutors
    ]

    await q.edit_message_text(
        LANG[lang]["tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ===============================
# Tyutor tanlash
# ===============================
async def choose_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    tutor_id = int(q.data.split("|")[1])
    context.user_data["tutor"] = tutor_id

    lang = context.user_data["lang"]

    await q.edit_message_text(LANG[lang]["write"])


# ===============================
# Savol qabul qilish
# ===============================
async def student_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    phone = context.user_data["phone"]
    lang = context.user_data["lang"]
    tutor_id = context.user_data["tutor"]
    fac_key = context.user_data["facet"]

    faculty_name = FACULTIES[fac_key][lang]

    # Guruhga yuborish
    msg = (
        f"📩 *Yangi savol!*\n"
        f"👤 [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 +{phone}\n"
        f"🏫 {faculty_name}\n"
        f"👨‍🏫 [Tyutor](tg://user?id={tutor_id})\n\n"
        f"💬 *Savol:* {text}"
    )

    await context.bot.send_message(
        TUTORS_GROUP_ID, msg, parse_mode="Markdown"
    )

    pending[user.id] = tutor_id

    await update.message.reply_text(LANG[lang]["sent"])
    await update.message.reply_text(LANG[lang]["done"])


# ===============================
# Tyutor reply qilganda
# ===============================
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutor = update.message.from_user

    for user_id, tid in pending.items():
        if tid == tutor.id:
            await context.bot.send_message(
                user_id,
                f"📨 *Tyutordan javob:*\n{update.message.text}",
                parse_mode="Markdown"
            )


# ===============================
# MAIN
# ===============================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_lang, pattern="^lang"))
    app.add_handler(CallbackQueryHandler(request_phone, pattern="^share"))
    app.add_handler(CallbackQueryHandler(choose_fac, pattern="^faculty"))
    app.add_handler(CallbackQueryHandler(choose_tutor, pattern="^tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, got_phone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, student_question))
    app.add_handler(MessageHandler(filters.REPLY, tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
