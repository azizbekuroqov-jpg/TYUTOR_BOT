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
BOT_TOKEN = "8368341342:AAEI1mEI17zWjOJYPogINydMQEIKE1XDLcE"  # ❗ TOKENNI KEYIN ALMASHTIRING
TUTORS_GROUP_ID = -1003374172310  # ❗ GURUH ID

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
        "start_first": "Avval /start ni bosib tilni tanlang."
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
        "start_first": "Сначала нажмите /start и выберите язык."
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
        "start_first": "Please press /start and choose a language first."
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
        "start_first": "Ilki bilen /start basyp dili saýlaň."
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
        "tutors": [{"name": "Хурсандова Дилафруз", "id": 8012275825}]
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
        # ⭐ Siz aytgandek nomini to‘g‘riladim:
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
            {"name": "Шодиеva Гулбахор", "id": 401016810},
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
    """
    - Kontakt orqali yuborilgan raqam HAR DOIM qabul qilinadi (state ga qaramay).
    - Matn bilan yozilgan raqam faqat state == 'phone' bo‘lsa ishlaydi.
    """

    lang = context.user_data.get("lang", "uz")
    t = LANG[lang]

    # 1) Kontakt keldi -> albatta qabul qilamiz
    if update.message.contact:
        phone = update.message.contact.phone_number

    # 2) Oddiy matn keldi -> faqat state == 'phone' bo‘lsa raqam sifatida qabul qilamiz
    else:
        if context.user_data.get("state") != "phone":
            # Bu text telefon emas, boshqa bosqichdagi matn bo‘lishi mumkin
            return

        raw = (update.message.text or "").strip()
        phone = raw.replace(" ", "").replace("-", "")
        if not phone or not phone.replace("+", "").isdigit():
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
    lang = context.user_data.get("lang", "uz")
    t = LANG[lang]

    context.user_data["faculty_key"] = fac_key
    faculty = FACULTIES[fac_key]
    tutors = faculty["tutors"]

    if not tutors:
        # Tyutor yo‘q → to‘g‘ri savolga o‘tamiz
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
# TUTOR SELECTED
# =====================
async def choose_tutor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    tutor_id = int(q.data.split("|")[1])
    context.user_data["tutor_id"] = tutor_id
    context.user_data["state"] = "question"

    lang = context.user_data.get("lang", "uz")
    t = LANG[lang]

    await q.message.reply_text(t["question"])

# =====================
# QUESTION RECEIVED
# =====================
async def question_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # faqat savol bosqichida ishlaydi
    if context.user_data.get("state") != "question":
        return

    user = update.message.from_user
    lang = context.user_data.get("lang", "uz")
    t = LANG[lang]

    phone = context.user_data.get("phone", "—")
    fac_key = context.user_data.get("faculty_key")
    faculty = FACULTIES[fac_key][lang] if fac_key else "—"

    tutor_id = context.user_data.get("tutor_id")
    tutor_name = None
    if tutor_id and fac_key:
        for f in FACULTIES[fac_key]["tutors"]:
            if f["id"] == tutor_id:
                tutor_name = f["name"]

    qtext = update.message.text

    student_link = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name or "Talaba")}</a>'
    tutor_link = (
        f'<a href="tg://user?id={tutor_id}">{html.escape(tutor_name)}</a>' if tutor_id and tutor_name else "—"
    )

    msg = (
        "📩 Yangi savol!\n"
        f"👤 Talaba: {student_link}\n"
        f"📞 {phone}\n"
        f"🏫 Fakulteti: {faculty}\n"
        f"👨‍🏫 Tyutor: {tutor_link}\n\n"
        f"💬 Savol: {html.escape(qtext)}"
    )

    try:
        sent = await context.bot.send_message(
            TUTORS_GROUP_ID, msg, parse_mode="HTML"
        )

        # javobni bog‘lash
        pending_messages[sent.message_id] = {"user_id": user.id, "lang": lang}

        await update.message.reply_text(t["sent"])
    except Exception as e:
        logger.exception("Guruhga habar yuborishda xato: %s", e)
        await update.message.reply_text(
            "❗ Savolingizni yuborishda texnik xato yuz berdi.\n"
            "Iltimos, birozdan so‘ng qayta urinib ko‘ring yoki tyutor bilan bevosita bog‘laning."
        )

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

    full_name = tutor.first_name or ""
    if tutor.last_name:
        full_name += f" {tutor.last_name}"

    await context.bot.send_message(
        user_id,
        f"👨‍🏫 {full_name}:\n{ans}"
    )

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

    lang = context.user_data.get("lang", "uz")
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

    # PRIVATE:
    # 1) Kontakt yuborilsa -> phone_handler
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.CONTACT, phone_handler))
    # 2) Matn yuborilsa:
    #    avval question_handler (agar state == 'question' bo‘lsa),
    #    keyin phone_handler (agar state == 'phone' bo‘lsa)
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, question_handler))
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND, phone_handler))

    # GROUP: tyutorlar javobi
    app.add_handler(MessageHandler(filters.Chat(TUTORS_GROUP_ID) & filters.TEXT & ~filters.COMMAND, tutor_reply))

    app.run_polling()

if __name__ == "__main__":
    main()
