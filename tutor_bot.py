import logging
import html
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# =====================
# CONFIG
# =====================
BOT_TOKEN = "8368341342:AAEI1mEI17zWjOJYPogINydMQEIKE1XDLcE"           # 🔥 O'ZGARTIRING
TUTORS_GROUP_ID = -1003374172310       # 🔥 O'ZGARTIRING

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =====================
# TIL PAKETI
# =====================
LANG = {
    "uz": {
        "start": "Assalomu alaykum!\nTilni tanlang:",
        "phone": "📱 Telefon raqamingizni ulashing yoki kiriting:",
        "phone_ok": "✅ Raqam qabul qilindi.",
        "faculty": "🏫 Fakultetingizni tanlang:",
        "tutor": "👨‍🏫 Tyutorni tanlang:",
        "question": "✍️ Savolingizni yozing:",
        "sent": "✔ Savolingiz yuborildi!\n⏳ Tez orada javob beramiz.",
        "again": "➕ Yana savol berish",
        "again_msg": "Yana savol bermoqchimisiz?",
        "err_phone": "❗ Telefon raqami noto‘g‘ri."
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "phone": "📱 Отправьте ваш номер:",
        "phone_ok": "✅ Номер принят.",
        "faculty": "🏫 Выберите факультет:",
        "tutor": "👨‍🏫 Выберите тьютора:",
        "question": "✍️ Введите свой вопрос:",
        "sent": "✔ Ваш вопрос отправлен!\n⏳ Скоро ответим.",
        "again": "➕ Задать ещё вопрос",
        "again_msg": "Хотите задать еще вопрос?",
        "err_phone": "❗ Неверный номер."
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "phone": "📱 Share or type your phone number:",
        "phone_ok": "✅ Phone saved.",
        "faculty": "🏫 Select faculty:",
        "tutor": "👨‍🏫 Select tutor:",
        "question": "✍️ Write your question:",
        "sent": "✔ Sent!\n⏳ Tutors will reply soon.",
        "again": "➕ Ask another question",
        "again_msg": "Want to ask another question?",
        "err_phone": "❗ Invalid phone number."
    },
    "tm": {
        "start": "Salam!\nDili saýlaň:",
        "phone": "📱 Telefon belgisiňiz giriziň:",
        "phone_ok": "✅ Kabul edildi.",
        "faculty": "🏫 Fakulteti saýlaň:",
        "tutor": "👨‍🏫 Tyutor saýlaň:",
        "question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Ugratdyk!\n⏳ Jogap geler.",
        "again": "➕ Ýene sorag bermek",
        "again_msg": "Ýene sorag bermek isleýärsiňizmi?",
        "err_phone": "❗ Telefon nädogry."
    }
}

# =====================
# FAKULTETLAR
# =====================
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [{"name": "Хурсандова Дилафруз", "id": 6939098356}]
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "ru": "Экология и право",
        "en": "Ecology & Law",
        "tm": "Ekologiýa we hukuk",
        "tutors": [
            {"name": "Ахмедова Ирода", "id": 6926132637},
            {"name": "Шоназаров Акбар", "id": 2052678760},
            {"name": "Саидова Хурсаной", "id": 702931087},
            {"name": "Худойназарова Дилнавоз", "id": 310033808},
        ]
    },
    "mech": {
        "uz": "Mexanizatsiya",
        "ru": "Механизация",
        "en": "Mechanization",
        "tm": "Mehanizasiýa",
        "tutors": []
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy",
        "tm": "Energetika",
        "tutors": [{"name": "Абдуллаев Ботир", "id": 485351327}]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Кадастр",
        "en": "Land & Cadastre",
        "tm": "Ýer kadastry",
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
        "tutors": [{"name": "Ахмеджанова Гулчеҳра", "id": 503802473}]
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

# pending_messages[msg_id] = {"user": ..., "lang": ...}
pending_messages = {}

# =====================
# START
# =====================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data["state"] = "lang"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ])

    await update.message.reply_text("Assalomu alaykum!\nTilni tanlang:", reply_markup=kb)

# =====================
# LANGUAGE CHOSEN
# =====================
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang
    context.user_data["state"] = "phone"

    t = LANG[lang]

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )

    await q.message.reply_text(t["phone"], reply_markup=kb)

# =====================
# PHONE HANDLER
# =====================
async def phone_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "phone":
        return

    lang = context.user_data["lang"]
    t = LANG[lang]

    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text.replace(" ", "").replace("-", "")
        if not phone.replace("+","").isdigit():
            await update.message.reply_text(t["err_phone"])
            return

    context.user_data["phone"] = phone
    context.user_data["state"] = "faculty"

    await update.message.reply_text(t["phone_ok"], reply_markup=ReplyKeyboardRemove())

    # Fakultetlar menyusi
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(fac[lang], callback_data=f"fac|{key}")]
        for key, fac in FACULTIES.items()
    ])
    await update.message.reply_text(t["faculty"], reply_markup=kb)

# =====================
# FACULTY SELECTED
# =====================
async def choose_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    fac_key = q.data.split("|")[1]
    lang = context.user_data["lang"]
    t = LANG[lang]

    context.user_data["faculty_key"] = fac_key
    faculty = FACULTIES[fac_key]
    tutors = faculty["tutors"]

    if not tutors:
        # Tyutor yo‘q → to‘g‘ri savol
        context.user_data["state"] = "question"
        await q.message.reply_text(t["question"])
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{t['id']}")]
        for t in tutors
    ])

    context.user_data["state"] = "tutor"
    await q.message.reply_text(t["tutor"], reply_markup=kb)

# =====================
# TUTOR SELECTED
# =====================
async def choose_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    tutor_id = int(q.data.split("|")[1])
    context.user_data["tutor_id"] = tutor_id
    context.user_data["state"] = "question"

    lang = context.user_data["lang"]
    t = LANG[lang]

    await q.message.reply_text(t["question"])

# =====================
# QUESTION RECEIVED
# =====================
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "question":
        return

    user = update.message.from_user
    lang = context.user_data["lang"]
    t = LANG[lang]

    phone = context.user_data["phone"]
    fac_key = context.user_data["faculty_key"]
    faculty = FACULTIES[fac_key][lang]

    tutor_id = context.user_data.get("tutor_id")
    tutor_name = None
    if tutor_id:
        for f in FACULTIES[fac_key]["tutors"]:
            if f["id"] == tutor_id:
                tutor_name = f["name"]

    qtext = update.message.text

    # Guruhga xabar
    student_link = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name)}</a>'
    tutor_link = (
        f'<a href="tg://user?id={tutor_id}">{tutor_name}</a>' if tutor_id else "—"
    )

    msg = (
        "📩 Yangi savol!\n"
        f"👤 Talaba: {student_link}\n"
        f"📞 {phone}\n"
        f"🏫 Fakulteti: {faculty}\n"
        f"👨‍🏫 Tyutor: {tutor_link}\n\n"
        f"💬 Savol: {html.escape(qtext)}"
    )

    sent = await context.bot.send_message(
        TUTORS_GROUP_ID, msg, parse_mode="HTML"
    )

    # javobni bog‘lash
    pending_messages[sent.message_id] = {"user_id": user.id, "lang": lang}

    await update.message.reply_text(t["sent"])
    context.user_data["state"] = "idle"

# =====================
# GROUP REPLY (Tutor → Student)
# =====================
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.chat_id != TUTORS_GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    orig_id = update.message.reply_to_message.message_id
    if orig_id not in pending_messages:
        return

    data = pending_messages[orig_id]
    user_id = data["user_id"]
    lang = data["lang"]
    t = LANG[lang]

    tutor = update.message.from_user
    ans = update.message.text

    full_name = tutor.first_name
    if tutor.last_name:
        full_name += f" {tutor.last_name}"

    await context.bot.send_message(
        user_id,
        f"👨‍🏫 {full_name}:\n{ans}"
    )

    # Yana savol
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(t["again"], callback_data="again")]
    ])
    await context.bot.send_message(user_id, t["again_msg"], reply_markup=kb)

    del pending_messages[orig_id]

# =====================
# AGAIN BUTTON
# =====================
async def again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = (
        context.user_data.get("lang")
        or LANG.keys().__iter__().__next__()   # fallback
    )
    t = LANG[lang]

    context.user_data["state"] = "faculty"

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(FACULTIES[key][lang], callback_data=f"fac|{key}")]
        for key in FACULTIES
    ])

    await q.message.reply_text(t["faculty"], reply_markup=kb)

# =====================
# MAIN
# =====================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_lang, pattern="^lang"))
    app.add_handler(CallbackQueryHandler(choose_faculty, pattern="^fac"))
    app.add_handler(CallbackQueryHandler(choose_tutor, pattern="^tutor"))
    app.add_handler(CallbackQueryHandler(again, pattern="^again$"))

    # Private
    app.add_handler(MessageHandler(filters.CONTACT, phone_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, phone_handler))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, question_handler))

    # Group reply
    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(TUTORS_GROUP_ID), tutor_reply))

    app.run_polling()

if __name__ == "__main__":
    main()
