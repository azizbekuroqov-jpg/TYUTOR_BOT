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
BOT_TOKEN = "8368341342:AAEI1mEI17zWjOJYPogINydMQEIKE1XDLcE"   # <-- tokeningiz
TUTORS_GROUP_ID = -1003374172310                              # <-- guruh ID

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
        "err_phone": "❗ Telefon raqami noto‘g‘ri.",
        "use_buttons": "Iltimos, tugmalardan foydalaning."
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
        "err_phone": "❗ Неверный номер.",
        "use_buttons": "Пожалуйста, используйте кнопки."
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
        "err_phone": "❗ Invalid phone number.",
        "use_buttons": "Please use the buttons."
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
        "err_phone": "❗ Telefon nädogry.",
        "use_buttons": "Düwmelerden peýdalanyň."
    }
}

# =====================
# FAKULTETLAR
# =====================
FACULTIES = {
    "hydraulic": {
        "uz": "Gidroteknika qurilishi",
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
        "uz": "Qishloq xo‘jaligini mexanizatsiyalash",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tm": "Oba hojalygyny mehanizasiýasynyň",
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

# msg_id -> {"user_id":..., "lang":...}
pending_messages = {}


# =====================
# HELPERS
# =====================
def get_lang(context: ContextTypes.DEFAULT_TYPE) -> str:
    return context.user_data.get("lang", "uz")


def T(context: ContextTypes.DEFAULT_TYPE, key: str) -> str:
    return LANG[get_lang(context)][key]


def faculties_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(fac[lang], callback_data=f"fac|{key}")]
        for key, fac in FACULTIES.items()
    ])


# =====================
# /start
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
# TIL TANLASH
# =====================
async def choose_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang
    context.user_data["state"] = "phone"

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await q.message.reply_text(LANG[lang]["phone"], reply_markup=kb)


# =====================
# TELEFON (CONTACT)
# =====================
async def phone_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "phone":
        return

    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone

    lang = get_lang(context)
    t = LANG[lang]

    context.user_data["state"] = "faculty"

    await update.message.reply_text(t["phone_ok"], reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(t["faculty"], reply_markup=faculties_keyboard(lang))


# =====================
# TELEFON (MATN)
# =====================
async def phone_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "phone":
        await update.message.reply_text(T(context, "use_buttons"))
        return

    lang = get_lang(context)
    t = LANG[lang]

    raw = (update.message.text or "").strip()
    phone = raw.replace(" ", "").replace("-", "")
    if not phone or not phone.replace("+", "").isdigit():
        await update.message.reply_text(t["err_phone"])
        return

    context.user_data["phone"] = phone
    context.user_data["state"] = "faculty"

    await update.message.reply_text(t["phone_ok"], reply_markup=ReplyKeyboardRemove())
    await update.message.reply_text(t["faculty"], reply_markup=faculties_keyboard(lang))


# =====================
# FAKULTET TANLASH
# =====================
async def choose_faculty(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") not in ("faculty", "again_faculty"):
        await update.callback_query.answer()
        return

    q = update.callback_query
    await q.answer()

    fac_key = q.data.split("|")[1]
    context.user_data["faculty_key"] = fac_key

    lang = get_lang(context)
    t = LANG[lang]

    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        context.user_data["tutor_id"] = None
        context.user_data["state"] = "question"
        await q.message.reply_text(t["question"])
        return

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton(tut["name"], callback_data=f"tutor|{tut['id']}")]
        for tut in tutors
    ])

    context.user_data["state"] = "tutor"
    await q.message.reply_text(t["tutor"], reply_markup=kb)


# =====================
# TUTOR TANLASH
# =====================
async def choose_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "tutor":
        await update.callback_query.answer()
        return

    q = update.callback_query
    await q.answer()

    tutor_id = int(q.data.split("|")[1])
    context.user_data["tutor_id"] = tutor_id
    context.user_data["state"] = "question"

    await q.message.reply_text(T(context, "question"))


# =====================
# SAVOL → GURUH
# =====================
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "question":
        await update.message.reply_text(T(context, "use_buttons"))
        return

    user = update.message.from_user
    phone = context.user_data.get("phone", "—")
    fac_key = context.user_data.get("faculty_key")
    lang = get_lang(context)

    if fac_key and fac_key in FACULTIES:
        faculty_name = FACULTIES[fac_key][lang]
    else:
        faculty_name = "—"

    tutor_id = context.user_data.get("tutor_id")
    tutor_name = None
    if tutor_id and fac_key and fac_key in FACULTIES:
        for tut in FACULTIES[fac_key]["tutors"]:
            if tut["id"] == tutor_id:
                tutor_name = tut["name"]
                break

    qtext = update.message.text

    student_link = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "Talaba")}</a>'
    tutor_link = (
        f'<a href="tg://user?id={tutor_id}">{html.escape(tutor_name)}</a>'
        if tutor_name else "—"
    )

    msg = (
        "📩 Yangi savol!\n"
        f"👤 Talaba: {student_link}\n"
        f"📞 {phone}\n"
        f"🏫 Fakulteti: {faculty_name}\n"
        f"👨‍🏫 Tyutor: {tutor_link}\n\n"
        f"💬 Savol: {html.escape(qtext)}"
    )

    lang_code = get_lang(context)
    t = LANG[lang_code]

    try:
        sent = await context.bot.send_message(
            TUTORS_GROUP_ID, msg, parse_mode="HTML"
        )
        pending_messages[sent.message_id] = {"user_id": user.id, "lang": lang_code}
        await update.message.reply_text(t["sent"])
    except Exception as e:
        logger.exception("Guruhga habar yuborishda xato: %s", e)
        await update.message.reply_text(
            "❗ Savolingizni yuborishda texnik xato yuz berdi.\n"
            "Iltimos, keyinroq yana urinib ko‘ring."
        )

    context.user_data["state"] = "idle"


# =====================
# TUTOR → TALABA JAVOB
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

    full_name = tutor.first_name or ""
    if tutor.last_name:
        full_name += f" {tutor.last_name}"

    await context.bot.send_message(
        user_id,
        f"👨‍🏫 {full_name}:\n{ans}"
    )

    kb = InlineKeyboardMarkup([[InlineKeyboardButton(t["again"], callback_data="again")]])
    await context.bot.send_message(user_id, t["again_msg"], reply_markup=kb)

    del pending_messages[orig_id]


# =====================
# YANA SAVOL
# =====================
async def again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = get_lang(context)
    t = LANG[lang]

    context.user_data["state"] = "again_faculty"
    await q.message.reply_text(t["faculty"], reply_markup=faculties_keyboard(lang))


# =====================
# PRIVATE TEXT ROUTER
# =====================
async def private_text_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")

    if not state:
        await update.message.reply_text("Iltimos /start ni bosing.")
        return

    if state == "phone":
        await phone_text(update, context)
    else:
        # faculty / tutor / question / idle → savol deb ko‘ramiz
        await question_handler(update, context)


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

    # Private chat
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.CONTACT, phone_contact))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
                                   private_text_router))

    # Tutorlar guruhi
    app.add_handler(MessageHandler(filters.Chat(TUTORS_GROUP_ID) & filters.TEXT & ~filters.COMMAND,
                                   tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
