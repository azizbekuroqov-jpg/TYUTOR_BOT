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

BOT_TOKEN = "8368341342:AAFubPHLot6nOj4UupdkZzC1YD-5RO1_tp0"          # <-- O'Z BOT TOKENINGIZNI YOZING
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
        "lang_chosen": "Til tanlandi: 🇺🇿 O‘zbek",
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
        "invalid_phone": "❗ Telefon raqamini to‘g‘ri kiriting.",
        "phone_ok": "✅ Raqam qabul qilindi.",
        "media_from_tutor": "🔊 Tyutordan media xabar yuborildi.",
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "lang_chosen": "Язык выбран: 🇷🇺 Русский",
        "share_phone": "📱 Пожалуйста, отправьте свой номер или введите вручную:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите ваш вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьюторам!\n⏳ Скоро получите ответ.",
        "again": "➕ Хотите задать ещё вопрос?",
        "invalid_phone": "❗ Введите корректный номер телефона.",
        "phone_ok": "✅ Номер принят.",
        "media_from_tutor": "🔊 От тьютора отправлено медиа-сообщение.",
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "lang_chosen": "Language selected: 🇬🇧 English",
        "share_phone": "📱 Please share your phone number or type it manually:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select tutor:",
        "write_question": "✍️ Write your question:",
        "sent": "✔ Your question has been sent!\n⏳ Tutors will reply soon.",
        "again": "➕ Do you want to ask another question?",
        "invalid_phone": "❗ Please enter a valid phone number.",
        "phone_ok": "✅ Phone number saved.",
        "media_from_tutor": "🔊 A media message has been sent by the tutor.",
    },
    "tm": {
        "start": "Salam!\nDili saýlaň:",
        "lang_chosen": "Dil saýlandy: 🇹🇲 Türkmençe",
        "share_phone": "📱 Telefon belgiňiz paýlaşyň ýa-da el bilen ýazyň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Tyutory saýlaň:",
        "write_question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy!\n⏳ Jogap gysga wagtda gelýär.",
        "again": "➕ Ýene-de sorag bermek isleýärsiňizmi?",
        "invalid_phone": "❗ Telefon belgiňiz dogry däl.",
        "phone_ok": "✅ Telefon belgiňiz kabul edildi.",
        "media_from_tutor": "🔊 Tyutordan media habary ugradyldy.",
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
            {"name": "Хурсандова Дилафруз", "id": 6939098356},
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
        "uz": "Qishloq xo‘jaligini mexanizatsiyalash",
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
        "ru": "Земельные resursy i kadastr",
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
            {"name": "Ахмеджанова Гулчеҳra", "id": 503802473},
        ],
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"name": "Эгамова Дильбар", "id": 115619153},
            {"name": "Шодиева Гулbahor", "id": 401016810},
        ],
    },
}

# Guruhdagi savol xabari ID → {"user_id": ..., "lang": ...}
pending_questions: dict[int, dict] = {}


# =======================
# HELP FUNKSIYALAR
# =======================

def make_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
            [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
            [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
            [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
        ]
    )


def make_faculty_keyboard(lang: str) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]
    return InlineKeyboardMarkup(keyboard)


# =======================
# /start
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    context.user_data.clear()
    context.user_data["state"] = "await_lang"

    await update.message.reply_text(
        LANG_PACK["uz"]["start"],
        reply_markup=make_lang_keyboard(),
    )


# =======================
# Til tanlash
# =======================
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, lang = query.data.split("|")
    if lang not in LANG_PACK:
        lang = "uz"

    context.user_data["lang"] = lang
    context.user_data["state"] = "await_phone"

    t = LANG_PACK[lang]

    await query.edit_message_text(t["lang_chosen"])

    phone_btn_text = {
        "uz": "📱 Raqamni ulashish",
        "ru": "📱 Поделиться номером",
        "en": "📱 Share phone number",
        "tm": "📱 Telefon belgimi paýlaş",
    }.get(lang, "📱 Raqamni ulashish")

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(phone_btn_text, request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    await query.message.reply_text(t["share_phone"], reply_markup=kb)


# =======================
# PRIVAT CHAT – TEXT + CONTACT
# =======================
async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    msg = update.message
    state = context.user_data.get("state")
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    # 1) AGAR CONTACT KELGAN BO'LSA – HAR QANDAY HOLATDA TELEFON DEB QABUL QILAMIZ
    if msg.contact:
        phone = msg.contact.phone_number
        context.user_data["phone"] = phone
        context.user_data["state"] = "await_faculty"

        await msg.reply_text(
            t["phone_ok"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await msg.reply_text(
            t["choose_faculty"],
            reply_markup=make_faculty_keyboard(lang),
        )
        return

    # Keyingi holatlar faqat text uchun
    if not msg.text:
        return

    text = msg.text.strip()

    # 2) Telefon qo‘lda kiritilsa
    if state == "await_phone":
        phone = text
        clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not clean.isdigit() or len(clean) < 7:
            await msg.reply_text(t["invalid_phone"])
            return

        context.user_data["phone"] = phone
        context.user_data["state"] = "await_faculty"

        await msg.reply_text(
            t["phone_ok"],
            reply_markup=ReplyKeyboardRemove(),
        )
        await msg.reply_text(
            t["choose_faculty"],
            reply_markup=make_faculty_keyboard(lang),
        )
        return

    # 3) Savol yozish bosqichi
    if state == "await_question":
        await handle_student_question(update, context)
        return

    # Boshqa holatlarda jim turamiz


# =======================
# Fakultet menyusi
# =======================
async def show_faculty_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    await update.message.reply_text(
        t["choose_faculty"],
        reply_markup=make_faculty_keyboard(lang),
    )


# =======================
# Fakultet tanlandi
# =======================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key = query.data.split("|")
    if fac_key not in FACULTIES:
        return

    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    context.user_data["faculty_key"] = fac_key
    faculty_name = FACULTIES[fac_key][lang]
    context.user_data["faculty_name"] = faculty_name

    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        context.user_data["selected_tutor_id"] = None
        context.user_data["selected_tutor_name"] = "Tyutor (biriktirilmagan)"
        context.user_data["state"] = "await_question"
        await query.edit_message_text(t["write_question"])
        return

    keyboard = [
        [InlineKeyboardButton(tu["name"], callback_data=f"tutor|{fac_key}|{tu['id']}")]
        for tu in tutors
    ]

    context.user_data["state"] = "await_tutor"

    await query.edit_message_text(
        t["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# =======================
# Tyutor tanlandi
# =======================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        _, fac_key, tutor_id = query.data.split("|")
        tutor_id = int(tutor_id)
    except Exception:
        return

    if fac_key not in FACULTIES:
        return

    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    context.user_data["faculty_name"] = FACULTIES[fac_key][lang]

    tutor_name = next(
        (tu["name"] for tu in FACULTIES[fac_key]["tutors"] if tu["id"] == tutor_id),
        None,
    )
    if tutor_name is None:
        return

    context.user_data["selected_tutor_id"] = tutor_id
    context.user_data["selected_tutor_name"] = tutor_name
    context.user_data["state"] = "await_question"

    await query.edit_message_text(t["write_question"])


# =======================
# Talaba savolini qabul qilish
# =======================
async def handle_student_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "await_question":
        return

    user = update.message.from_user
    question = update.message.text

    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    phone = context.user_data.get("phone", "Noma'lum")
    faculty_name = context.user_data.get("faculty_name", "Noma'lum")
    tutor_id = context.user_data.get("selected_tutor_id")
    tutor_name = context.user_data.get("selected_tutor_name", "Noma'lum")

    student_full_name = (user.first_name or "") + (
        f" {user.last_name}" if user.last_name else ""
    )
    student_mention = f'<a href="tg://user?id={user.id}">{html.escape(student_full_name.strip() or "Talaba")}</a>'

    if tutor_id:
        tutor_mention = f'<a href="tg://user?id={tutor_id}">{html.escape(tutor_name)}</a>'
    else:
        tutor_mention = html.escape(tutor_name)

    username_part = f" (@{user.username})" if user.username else ""

    text = (
        "📩 <b>Yangi savol!</b>\n\n"
        f"👤 Talaba: {student_mention}{html.escape(username_part)}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"📞 Telefon: {html.escape(phone)}\n"
        f"🏫 Fakulteti: {html.escape(faculty_name)}\n"
        f"👨‍🏫 Tyutor: {tutor_mention}\n\n"
        f"💬 Savol:\n<blockquote>{html.escape(question)}</blockquote>"
    )

    sent = await context.bot.send_message(
        TUTORS_GROUP_ID,
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
    )

    pending_questions[sent.message_id] = {"user_id": user.id, "lang": lang}

    await update.message.reply_text(t["sent"])

    context.user_data["state"] = "idle"


# =======================
# Guruhda tyutor javobi (reply)
# =======================
async def tutor_group_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != TUTORS_GROUP_ID:
        return

    msg = update.message
    if not msg.reply_to_message:
        return

    original_id = msg.reply_to_message.message_id
    info = pending_questions.get(original_id)
    if not info:
        return

    user_id = info["user_id"]
    lang = info.get("lang", "uz")
    t = LANG_PACK.get(lang, LANG_PACK["uz"])

    tutor = msg.from_user
    answer_text = msg.text or msg.caption
    if not answer_text:
        answer_text = t["media_from_tutor"]

    full_name = tutor.first_name or ""
    if tutor.last_name:
        full_name += f" {tutor.last_name}"
    if tutor.username:
        full_name += f" (@{tutor.username})"

    reply_for_student = f"👨‍🏫 {full_name}:\n\n{answer_text}"

    try:
        await context.bot.send_message(user_id, reply_for_student)
    except Exception as e:
        logger.error("Talabaga javob yuborishda xato: %s", e)

    keyboard = [
        [InlineKeyboardButton("➕ Yana savol berish", callback_data="again")]
    ]

    await context.bot.send_message(
        user_id,
        t["again"],
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

    pending_questions.pop(original_id, None)


# =======================
# "Yana savol berish" tugmasi
# =======================
async def ask_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    context.user_data["state"] = "await_faculty"

    await query.message.reply_text(
        t["choose_faculty"],
        reply_markup=make_faculty_keyboard(lang),
    )


# =======================
# MAIN
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern=r"^lang\|"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern=r"^faculty\|"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern=r"^tutor\|"))
    app.add_handler(CallbackQueryHandler(ask_again, pattern=r"^again$"))

    # Bitta handler — private chatdagi hamma text/contact shu yerga tushadi
    app.add_handler(
        MessageHandler(
            filters.ChatType.PRIVATE & ~filters.COMMAND,
            handle_private,
        )
    )

    app.add_handler(
        MessageHandler(
            filters.Chat(TUTORS_GROUP_ID)
            & ~filters.COMMAND
            & ~filters.StatusUpdate.ALL,
            tutor_group_reply,
        )
    )

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
