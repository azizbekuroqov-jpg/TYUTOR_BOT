import logging
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)

# ========================================================
# CONFIG
# ========================================================

BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
TUTORS_GROUP_ID = -1003374172310   # Siz bergan group ID

logging.basicConfig(level=logging.INFO)

# ========================================================
# 4 TA TIL UCHUN MATNLAR
# ========================================================

LANG = {
    "uz": {
        "hello": "Assalomu alaykum! Tilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing:",
        "choose_faculty": "🏫 Fakultetingizni tanlang:",
        "choose_tutor": "👨‍🏫 Tyutorni tanlang:",
        "write_question": "✍️ Savolingizni yozing:",
        "sent": "✔ Savolingiz tyutorlarga yuborildi! Tez orada sizga javob beramiz."
    },
    "ru": {
        "hello": "Здравствуйте! Выберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте свой номер телефона:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите свой вопрос:",
        "sent": "✔ Ваш вопрос отправлен! Мы скоро ответим."
    },
    "en": {
        "hello": "Hello! Choose your language:",
        "share_phone": "📱 Please share your phone number:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select your tutor:",
        "write_question": "✍️ Write your question:",
        "sent": "✔ Your question has been sent! We will reply soon."
    },
    "tm": {
        "hello": "Salam! Dili saýlaň:",
        "share_phone": "📱 Telefon belgiňizi paýlaşyň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Mugallymy saýlaň:",
        "write_question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy! Ýakynda jogap bereris."
    }
}

# ========================================================
# 7 TA FAKULTET + TUTORLAR
# ========================================================

FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [
            {"id": 6939098356, "name": "Хурсандова Дилафруз"},
        ]
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "ru": "Экология и право",
        "en": "Ecology and Law",
        "tm": "Ekologiýa we hukuk",
        "tutors": [
            {"id": 6926132637, "name": "Ахмедова Ирода"},
            {"id": 2052678760, "name": "Шоназаров Акбар"},
            {"id": 702931087, "name": "Саидова Хурсаной"},
            {"id": 310033808, "name": "Худойназарова Дилнавоз"},
        ]
    },
    "mechanization": {
        "uz": "Qishloq xo‘jaligini mexanizatsiyalash",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tm": "Oba hojalygyny mehanizasiýa",
        "tutors": []
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tm": "Energetika",
        "tutors": [
            {"id": 485351327, "name": "Абдуллаев Ботир"},
        ]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources and Cadastre",
        "tm": "Ýer serişdeleri we kadastr",
        "tutors": [
            {"id": 8376601534, "name": "Турғунова Мафтуна"},
            {"id": 2134838705, "name": "Абдуллаева Олия"},
        ]
    },
    "hydromelioration": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tm": "Gidromeliorasiýa",
        "tutors": [
            {"id": 503802473, "name": "Ахмеджанова Гулчеҳра"},
        ]
    },
    "economics": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"id": 115619153, "name": "Эгамова Дилбар"},
            {"id": 1720369159, "name": "Шодиева Гулбахор"},
        ]
    }
}

# Talabalar savoli → tyutor javobi uchun saqlanadi
pending_answers = {}

# ========================================================
# START
# ========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang_tm")],
    ]
    await update.message.reply_text(
        "Assalomu alaykum! Tilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========================================================
# LANGUAGE SELECTED
# ========================================================

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("_")[1]
    context.user_data["lang"] = lang

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

    await q.message.reply_text(
        LANG[lang]["share_phone"],
        reply_markup=kb
    )

# ========================================================
# CONTACT HANDLING
# ========================================================

async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number

    context.user_data["phone"] = phone

    lang = context.user_data["lang"]

    await update.message.reply_text("✔ Raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())

    # Fakultetlar menyusi
    keyboard = []
    for key, fac in FACULTIES.items():
        keyboard.append([InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")])

    await update.message.reply_text(
        LANG[lang]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========================================================
# FACULTY SELECTED
# ========================================================

async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    fac_key = q.data.split("|")[1]
    lang = context.user_data["lang"]

    context.user_data["faculty"] = FACULTIES[fac_key][lang]
    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        # Tyutor yo‘q → bevosita savol berilsin
        context.user_data["tutor_id"] = None
        context.user_data["tutor_name"] = "Tyutor mavjud emas"
        await q.message.reply_text(LANG[lang]["write_question"])
        return

    keyboard = []
    for t in tutors:
        keyboard.append([
            InlineKeyboardButton(t["name"], callback_data=f"tutor|{t['id']}|{t['name']}")
        ])

    await q.message.reply_text(
        LANG[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ========================================================
# TUTOR SELECTED
# ========================================================

async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    _, tid, tname = q.data.split("|")
    context.user_data["tutor_id"] = int(tid)
    context.user_data["tutor_name"] = tname

    lang = context.user_data["lang"]
    await q.message.reply_text(LANG[lang]["write_question"])

# ========================================================
# TALABA SAVOL YOZGANDA → GURUHGA YUBORILADI
# ========================================================

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    q = update.message.text

    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id = context.user_data["tutor_id"]
    tutor_name = context.user_data["tutor_name"]
    lang = context.user_data["lang"]

    # Guruhga xabar
    msg = await context.bot.send_message(
        TUTORS_GROUP_ID,
        f"📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}\n"
        f"🏫 Fakulteti: {faculty}\n\n"
        f"👨‍🏫 Tyutor: [{tutor_name}](tg://user?id={tutor_id})\n\n"
        f"💬 Savol: {q}",
        parse_mode="Markdown"
    )

    # Talabaga keyin yuborish uchun saqlaymiz
    pending_answers[msg.message_id] = {
        "user_id": user.id,
        "tutor_id": tutor_id
    }

    await update.message.reply_text(LANG[lang]["sent"])

# ========================================================
# TUTOR JAVOBI → TALABAGA
# ========================================================

async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != TUTORS_GROUP_ID:
        return

    tutor = update.message.from_user
    text = update.message.text

    # Tyutor ismni topamiz
    tutor_name = None
    for f in FACULTIES.values():
        for t in f["tutors"]:
            if t["id"] == tutor.id:
                tutor_name = t["name"]

    if not tutor_name:
        return  # Tyutor emas

    # Talabaga yuborish
    for question_msg_id, data in pending_answers.items():
        if data["tutor_id"] == tutor.id:
            user_id = data["user_id"]

            await context.bot.send_message(
                user_id,
                f"{tutor_name}: {text}"
            )
            return

# ========================================================
# MAIN
# ========================================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang_"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.ChatType.GROUPS, handle_question))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.GROUPS, tutor_reply))

    app.run_polling()

if __name__ == "__main__":
    main()
