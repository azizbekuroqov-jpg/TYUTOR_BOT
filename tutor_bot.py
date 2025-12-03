import logging
import html

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =======================
# CONFIG
# =======================

BOT_TOKEN = "8368341342:AAEI1mEI17zWjOJYPogINydMQEIKE1XDLcE"          # <-- O'Z BOT TOKENINGIZNI YOZING
TUTORS_GROUP_ID = -1003374172310           # <-- TYUTORLAR GURUHI ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# =======================
# TILLAR
# =======================

LANG_PACK = {
    "uz": {
        "start": "Assalomu alaykum!\nTilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing yoki qo‘lda kiriting:",
        "choose_faculty": "🏫 Fakultetingizni tanlang:",
        "choose_tutor": "👨‍🏫 Tyutorni tanlang:",
        "write_question": "✍️ Savolingizni yozing:",
        "sent": (
            "✔ Savolingiz tyutorlarga yuborildi!\n"
            "⏳ Tez orada javob beramiz.\n"
            "Murojaatingiz uchun rahmat!"
        ),
        "again": "➕ Yana savol bermoqchimisiz?",
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте свой номер или введите вручную:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите свой вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьюторам!\n⏳ Скоро получите ответ.",
        "again": "➕ Хотите задать ещё вопрос?",
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "share_phone": "📱 Please share your phone number or type it manually:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select tutor:",
        "write_question": "✍️ Write your question:",
        "sent": "✔ Your question has been sent!\n⏳ Tutors will reply soon.",
        "again": "➕ Do you want to ask another question?",
    },
    "tm": {
        "start": "Salam!\nDili saýlaň:",
        "share_phone": "📱 Telefon belgiňiz paýlaşyň ýa-da el bilen ýazyň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Tyutory saýlaň:",
        "write_question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy!\n⏳ Jogap gysga wagtda gelýär.",
        "again": "➕ Ýene-de sorag bermek isleýärsiňizmi?",
    },
}

# =======================
# FAKULTETLAR + TYUTORLAR
# =======================

FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [
            {"name": "Хурсандова Дилафруз", "id": 1720369159},
        ],
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
        ],
    },
    "mech": {
        "uz": "Mexanizatsiya",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tm": "Mehanizasiýa",
        "tutors": [],
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tm": "Energetika",
        "tutors": [
            {"name": "Абдуллаев Ботир", "id": 485351327},
        ],
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources and Cadastre",
        "tm": "Ýer serişdeleri we kadastr",
        "tutors": [
            {"name": "Турғунова Мафтуна", "id": 8376601534},
            {"name": "Абдуллаева Олия", "id": 2134838705},
        ],
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tm": "Gidromeliorasiýa",
        "tutors": [
            {"name": "Ахмеджанова Гулчеҳра", "id": 503802473},
        ],
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"name": "Эгамова Дильбар", "id": 115619153},
            {"name": "Шодиева Гулбахор", "id": 401016810},
        ],
    },
}

# Guruhdagi savol xabari ID → talaba ID
pending_questions: dict[int, int] = {}


# =======================
# /start
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Har safar /start bo‘lsa — user uchun holatni tozalaymiz
    context.user_data.clear()
    context.user_data["state"] = "await_lang"

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]

    await update.message.reply_text(
        "Assalomu alaykum!\nTilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


def make_lang_keyboard():
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
            [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
        ]
    )


# =======================
# Til tanlash
# =======================
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("|")[1]
    context.user_data["lang"] = lang
    context.user_data["state"] = "await_phone"

    text = LANG_PACK[lang]

    # Telefon uchun tugma — faqat shu yerda chiqadi
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await query.edit_message_text(text["start"])
    await query.message.reply_text(text["share_phone"], reply_markup=kb)


# =======================
# Telefon (contact) – faqat PHONE bosqichida
# =======================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "await_phone":
        return

    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone
    context.user_data["state"] = "await_faculty"

    # Telefon tugmasini yo‘qotamiz
    await update.message.reply_text("✅ Raqam qabul qilindi.", reply_markup=ReplyKeyboardRemove())

    await show_faculty_menu(update, context)


# =======================
# Private text – telefon yoki savol
# =======================
async def handle_private_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get("state")

    # 1) Telefon qo‘lda kiritish
    if state == "await_phone":
        phone = update.message.text.strip()
        clean = phone.replace("+", "").replace(" ", "")
        if not clean.isdigit():
            await update.message.reply_text("❗ Telefon raqamini to‘g‘ri kiriting.")
            return

        context.user_data["phone"] = phone
        context.user_data["state"] = "await_faculty"

        # Telefon tugmasini yo‘qotamiz
        await update.message.reply_text("✅ Raqam qabul qilindi.", reply_markup=ReplyKeyboardRemove())

        await show_faculty_menu(update, context)
        return

    # 2) Savol yozish bosqichi
    if state == "await_question":
        await handle_student_question(update, context)
        return

    # Boshqa hollarda — hech narsa qilmaymiz (bot jim)


# =======================
# Fakultet menyusi
# =======================
async def show_faculty_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    text = LANG_PACK[lang]["choose_faculty"]

    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


# =======================
# Fakultet tanlandi
# =======================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    fac_key = query.data.split("|")[1]
    lang = context.user_data.get("lang", "uz")

    context.user_data["faculty_key"] = fac_key
    faculty_name = FACULTIES[fac_key][lang]
    context.user_data["faculty_name"] = faculty_name

    tutors = FACULTIES[fac_key]["tutors"]

    # Agar tyutor bo‘lmasa — to‘g‘ridan-to‘g‘ri savol
    if not tutors:
        context.user_data["state"] = "await_question"
        await query.edit_message_text(LANG_PACK[lang]["write_question"])
        return

    # Tyutorlar menyusi
    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{fac_key}|{t['id']}")]
        for t in tutors
    ]

    context.user_data["state"] = "await_tutor"

    await query.edit_message_text(
        LANG_PACK[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =======================
# Tyutor tanlandi
# =======================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key, tutor_id = query.data.split("|")
    tutor_id = int(tutor_id)
    lang = context.user_data.get("lang", "uz")

    # Fakultet nomini ham qayta aniq saqlaymiz
    context.user_data["faculty_name"] = FACULTIES[fac_key][lang]

    tutor_name = next(
        t["name"] for t in FACULTIES[fac_key]["tutors"] if t["id"] == tutor_id
    )

    context.user_data["selected_tutor_id"] = tutor_id
    context.user_data["selected_tutor_name"] = tutor_name
    context.user_data["state"] = "await_question"

    await query.edit_message_text(LANG_PACK[lang]["write_question"])


# =======================
# Talaba savolini qabul qilish
# =======================
async def handle_student_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat to‘g‘ri bosqichda ishlasin
    if context.user_data.get("state") != "await_question":
        return

    user = update.message.from_user
    question = update.message.text

    phone = context.user_data.get("phone", "Noma'lum")
    faculty_name = context.user_data.get("faculty_name", "Noma'lum")
    tutor_id = context.user_data.get("selected_tutor_id")
    tutor_name = context.user_data.get("selected_tutor_name", "Noma'lum")
    lang = context.user_data.get("lang", "uz")

    # CLICKABLE mentionlar — HTML
    student_mention = f'<a href="tg://user?id={user.id}">{html.escape(user.first_name)}</a>'
    if tutor_id:
        tutor_mention = f'<a href="tg://user?id={tutor_id}">{html.escape(tutor_name)}</a>'
    else:
        tutor_mention = html.escape(tutor_name)

    text = (
        "📩 Yangi savol!\n"
        f"👤 Talaba: {student_mention}\n"
        f"📞 {html.escape(phone)}\n"
        f"🏫 Fakulteti: {html.escape(faculty_name)}\n\n"
        f"👨‍🏫 Tyutor: {tutor_mention}\n\n"
        f"💬 Savol: {html.escape(question)}"
    )

    sent = await context.bot.send_message(
        TUTORS_GROUP_ID, text, parse_mode="HTML"
    )

    # Bu guruh xabariga reply qilinsa — qaysi talabaga tegishli ekanini bilamiz
    pending_questions[sent.message_id] = user.id

    await update.message.reply_text(LANG_PACK[lang]["sent"])

    # Savoldan keyin holatni "tayyor" qilib qo‘yamiz
    context.user_data["state"] = "idle"


# =======================
# Guruhda tyutor javobi (reply)
# =======================
async def tutor_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Faqat tyutorlar guruhi
    if update.message.chat_id != TUTORS_GROUP_ID:
        return

    if not update.message.reply_to_message:
        return

    original_id = update.message.reply_to_message.message_id
    user_id = pending_questions.get(original_id)
    if not user_id:
        return

    tutor = update.message.from_user
    answer_text = update.message.text or update.message.caption
    if not answer_text:
        answer_text = "🔊 Tyutordan media xabar yuborildi."

    full_name = tutor.first_name or ""
    if tutor.last_name:
        full_name += f" {tutor.last_name}"

    msg = f"👨‍🏫 {full_name}: {answer_text}"

    try:
        await context.bot.send_message(user_id, msg)
    except Exception as e:
        logger.error("Talabaga javob yuborishda xato: %s", e)

    # Talabaga "yana savol berish" tugmasi
    lang = "uz"  # agar user_data bo‘lmasa ham default
    keyboard = [
        [InlineKeyboardButton("➕ Yana savol berish", callback_data="again")]
    ]

    await context.bot.send_message(
        user_id,
        LANG_PACK[lang]["again"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    # Bu savol bo‘yicha mappingni o‘chirib tashlaymiz
    pending_questions.pop(original_id, None)


# =======================
# "Yana savol berish" tugmasi
# =======================
async def ask_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Holatni qayta fakultet tanlashga qaytaramiz
    lang = context.user_data.get("lang", "uz")
    context.user_data["state"] = "await_faculty"

    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await query.message.reply_text(
        LANG_PACK[lang]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # Private chat
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="^lang\\|"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="^faculty\\|"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="^tutor\\|"))
    app.add_handler(CallbackQueryHandler(ask_again, pattern="^again$"))

    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.CONTACT,
            handle_contact,
        )
    )
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & filters.TEXT & ~filters.COMMAND,
            handle_private_text,
        )
    )

    # Guruhdagi tyutor javoblari
    app.add_handler(
        MessageHandler(
            filters.Chat(TUTORS_GROUP_ID)
            & ~filters.COMMAND
            & ~filters.StatusUpdate.ALL,
            tutor_group_reply,
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
