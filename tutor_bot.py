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

# =======================
# CONFIG
# =======================

BOT_TOKEN = "YOUR_BOT_TOKEN"
TUTORS_GROUP_ID = -1003374172310  # Siz yuborgan ID

logging.basicConfig(level=logging.INFO)

# =======================
# LANGUAGE PACK
# =======================

LANG_PACK = {
    "uz": {
        "start": "Assalomu alaykum!\nTilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing yoki qo‘lda kiriting:",
        "choose_faculty": "🏫 Fakultetni tanlang:",
        "choose_tutor": "👨‍🏫 Tyutorni tanlang:",
        "write_question": "✍️ Savolingizni yozing:",
        "sent": "✔ Savolingiz tyutorlarga yuborildi!\n⏳ Tez orada javob berishadi.\nMurojaatingiz uchun rahmat!",
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "share_phone": "📱 Отправьте свой номер или введите вручную:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите свой вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьюторам!\n⏳ Ответ придет скоро.",
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "share_phone": "📱 Please share your phone number or type it manually:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select tutor:",
        "write_question": "✍️ Write your question:",
        "sent": "✔ Your question was sent!\n⏳ Tutors will reply soon.",
    },
    "tm": {
        "start": "Salam!\nDili saýlaň:",
        "share_phone": "📱 Telefon belginizi paýlaşyň ýa-da ýazyp goýuň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Tyutory saýlaň:",
        "write_question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Sorag ugradyldy!\n⏳ Ýakyn wagtda jogap berler.",
    }
}

# =======================
# FACULTIES
# =======================

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
            {"name": "Ахмедова Ирода", "id": 1720369159},
            {"name": "Шоназаров Акбар", "id": 2052678760},
            {"name": "Саидова Хурсаной", "id": 702931087},
            {"name": "Худойназарова Дилнавоз", "id": 310033808},
        ]
    },
    "mech": {
        "uz": "Mexanizatsiya",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tm": "Mehanizasiýa",
        "tutors": []
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tm": "Energetika",
        "tutors": [
            {"name": "Абдуллаев Ботир", "id": 485351327}
        ]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources & Cadastre",
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
            {"name": "Эгамова Дильбар", "id": 115619153},
            {"name": "Шодиева Гулбахор", "id": 401016810},
        ]
    }
}

# Mapping student → tutor
pending = {}


# =======================
# START
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]
    await update.message.reply_text(
        "Assalomu alaykum!\nTilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
# LANGUAGE SELECTED
# =======================
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("|")[1]
    context.user_data["lang"] = lang

    text = LANG_PACK[lang]

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

    await query.edit_message_text(text["share_phone"])
    await query.message.reply_text(text["share_phone"], reply_markup=kb)

    context.user_data["waiting_phone"] = True


# =======================
# UNIVERSAL PHONE CAPTURE
# =======================
async def handle_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        if not context.user_data.get("waiting_phone"):
            return
        phone = update.message.text

        if not phone.replace("+", "").replace(" ", "").isdigit():
            await update.message.reply_text("❗ Telefon raqamini to‘g‘ri kiriting.")
            return

    context.user_data["phone"] = phone
    context.user_data["waiting_phone"] = False

    lang = context.user_data["lang"]

    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG_PACK[lang]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
# FACULTY SELECT
# =======================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    fac_key = query.data.split("|")[1]
    lang = context.user_data["lang"]

    context.user_data["faculty"] = FACULTIES[fac_key][lang]

    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        await query.edit_message_text(LANG_PACK[lang]["write_question"])
        return

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{fac_key}|{t['id']}")]
        for t in tutors
    ]

    await query.edit_message_text(
        LANG_PACK[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
# TUTOR SELECTED
# =======================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key, tutor_id = query.data.split("|")
    tutor_id = int(tutor_id)

    lang = context.user_data["lang"]

    tutor_name = next(t["name"] for t in FACULTIES[fac_key]["tutors"] if t["id"] == tutor_id)

    context.user_data["tutor"] = (tutor_id, tutor_name)

    await query.edit_message_text(LANG_PACK[lang]["write_question"])


# =======================
# STUDENT QUESTION
# =======================
async def receive_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if "tutor" not in context.user_data:
        return

    user = update.message.from_user
    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id, tutor_name = context.user_data["tutor"]
    question = update.message.text
    lang = context.user_data["lang"]

    pending[tutor_id] = {
        "user_id": user.id,
        "name": user.first_name,
    }

    msg = (
        f"📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}\n"
        f"🏫 Fakultet: {faculty}\n"
        f"👨‍🏫 Tyutor: [{tutor_name}](tg://user?id={tutor_id})\n\n"
        f"💬 Savol:\n{question}"
    )

    await context.bot.send_message(TUTORS_GROUP_ID, msg, parse_mode="Markdown")

    await update.message.reply_text(LANG_PACK[lang]["sent"])


# =======================
# TUTOR REPLY
# =======================
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutor = update.message.from_user
    msg = update.message.text

    if tutor.id not in pending:
        return

    student = pending[tutor.id]

    await context.bot.send_message(
        student["user_id"],
        f"📨 *{tutor.first_name}:* {msg}",
        parse_mode="Markdown"
    )

    del pending[tutor.id]


# =======================
# RUN BOT
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, handle_phone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_phone))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, receive_question))
    app.add_handler(MessageHandler(filters.TEXT, tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
