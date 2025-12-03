import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
ADMIN_ID = 8012275825
TUTORS_GROUP_ID = -1003374172310

# 4 TIL UCHUN MATNLAR
LANG = {
    "uz": {
        "start": "Assalomu alaykum! Tilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing:",
        "choose_faculty": "Fakultetingizni tanlang:",
        "choose_tutor": "Tyutorni tanlang:",
        "write_question": "Savolingizni yozing:",
        "sent": "Savolingiz tyutorga yuborildi! Tez orada javob beramiz. Rahmat!"
    },
    "ru": {
        "start": "Здравствуйте! Выберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте номер телефона:",
        "choose_faculty": "Выберите факультет:",
        "choose_tutor": "Выберите тьютора:",
        "write_question": "Введите свой вопрос:",
        "sent": "Ваш вопрос отправлен! Мы скоро ответим."
    },
    "en": {
        "start": "Hello! Choose your language:",
        "share_phone": "📱 Please share your phone number:",
        "choose_faculty": "Select your faculty:",
        "choose_tutor": "Select your tutor:",
        "write_question": "Write your question:",
        "sent": "Your question has been sent! We will reply soon."
    },
    "tm": {
        "start": "Salam! Dili saýlaň:",
        "share_phone": "📱 Telefon belgiňizi paýlaşyň:",
        "choose_faculty": "Fakulteti saýlaň:",
        "choose_tutor": "Tyutory saýlaň:",
        "write_question": "Soragyňyzy ýazyň:",
        "sent": "Sorag ugradyldy! Jogap ýakynda."
    }
}

# 7 FAKULTET + TYUTORLAR
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [
            {"name": "Хурсандова Дилафруз", "id": 6939098356}
        ]
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "ru": "Экология и право",
        "en": "Ecology and Law",
        "tm": "Ekologiýa we hukuk",
        "tutors": [
            {"name": "Ахмедова Ирода", "id": 6926132637},
            {"name": "Шоназаров Акбар", "id": 2052678760},
            {"name": "Саидова Хурсаной", "id": 702931087},
            {"name": "Худойназарова Дилнавоз", "id": 310033808},
        ]
    },
    "mech": {
        "uz": "Q.X. Mexanizatsiya fakulteti",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tm": "Oba hojalygyny mehanizasiýa",
        "tutors": []
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy",
        "tm": "Energetika",
        "tutors": [
            {"name": "Абдуллаев Ботир", "id": 485351327}
        ]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources and Cadastre",
        "tm": "Ýer serişdeleri we kadastr",
        "tutors": [
            {"name": "Турғунова Мафтуна", "id": 8376601534},
            {"name": "Абдуллаева Олия", "id": 2134838705},
        ]
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tm": "Gidromeliorasiýa",
        "tutors": [
            {"name": "Ахмеджанова Гулчеҳра", "id": 503802473}
        ]
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"name": "Эгамова Дилбар", "id": 115619153},
            {"name": "Шодиеva Гулбахор", "id": 1720369159},
        ]
    }
}

pending_answers = {}

# START
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

# TIL TANLANGANDA
async def set_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

    await q.edit_message_text(LANG[lang]["share_phone"])
    await q.message.reply_text(LANG[lang]["share_phone"], reply_markup=kb)

# RAQAM QABUL QILINGANDA
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone
    lang = context.user_data["lang"]

    # klaviaturani yo‘qotish
    await update.message.reply_text("✔️", reply_markup=ReplyKeyboardMarkup([[" "]], resize_keyboard=True))

    # Fakultetlar menyusi
    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG[lang]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# FAKULTET TANLANGANDA
async def faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.split("|")[1]
    lang = context.user_data["lang"]

    tutors = FACULTIES[key]["tutors"]
    context.user_data["faculty"] = FACULTIES[key][lang]

    if len(tutors) == 0:
        await q.edit_message_text(LANG[lang]["write_question"])
        return

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{key}|{t['id']}")]
    for t in tutors]

    await q.edit_message_text(
        LANG[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# TUTOR TANLANGANDA
async def tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, fac_key, tutor_id = q.data.split("|")
    tutor_id = int(tutor_id)

    lang = context.user_data["lang"]

    tutor_name = ""
    for t in FACULTIES[fac_key]["tutors"]:
        if t["id"] == tutor_id:
            tutor_name = t["name"]

    context.user_data["selected_tutor"] = tutor_id
    context.user_data["selected_tutor_name"] = tutor_name

    await q.edit_message_text(LANG[lang]["write_question"])

# SAVOL QABUL QILINGANDA
async def ask(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    q = update.message.text

    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id = context.user_data["selected_tutor"]
    tutor_name = context.user_data["selected_tutor_name"]

    # Guruhga yuborish
    msg = await context.bot.send_message(
        TUTORS_GROUP_ID,
        f"📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}\n"
        f"🏫 Fakultet: {faculty}\n\n"
        f"👨‍🏫 Tyutor: [{tutor_name}](tg://user?id={tutor_id})\n\n"
        f"💬 Savol: {q}",
        parse_mode="Markdown"
    )

    pending_answers[msg.message_id] = {
        "user_id": user.id,
        "tutor_id": tutor_id
    }

    await update.message.reply_text(LANG[context.user_data["lang"]]["sent"])

# TUTOR JAVOBI – faqat REPLY bo‘lsa
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != TUTORS_GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    message_id = update.message.reply_to_message.message_id

    if message_id not in pending_answers:
        return

    data = pending_answers[message_id]
    text = update.message.text

    # tyutor ismini topish
    tutor_name = None
    for f in FACULTIES.values():
        for t in f["tutors"]:
            if t["id"] == update.message.from_user.id:
                tutor_name = t["name"]

    if not tutor_name:
        tutor_name = "Tyutor"

    await context.bot.send_message(
        data["user_id"],
        f"{tutor_name}: {text}"
    )

    del pending_answers[message_id]

# MAIN
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(set_lang, pattern="lang"))
    app.add_handler(MessageHandler(filters.CONTACT, get_phone))
    app.add_handler(CallbackQueryHandler(faculty, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor, pattern="tutor"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask))
    app.add_handler(MessageHandler(filters.TEXT, tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
