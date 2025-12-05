import logging
import html
import re

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
BOT_TOKEN = "8368341342:AAFubPHLot6nOj4UupdkZzC1YD-5RO1_tp0"       # <- bot tokeningiz
TUTORS_GROUP_ID = -1003374172310        # <- tyutorlar guruhi ID

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Guruh xabaridan talaba ID sini olish uchun
ID_RE = re.compile(r"\bID:\s*(\d+)\b")

# =======================
# TILLAR (UZ / RU / EN)
# =======================
LANG_PACK = {
    "uz": {
        "start": "Assalomu alaykum!\nTilni tanlang:",
        "lang_chosen": "Til tanlandi: 🇺🇿 O‘zbek",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing yoki qo‘lda kiriting:",
        "choose_faculty": "🏫 Fakultetingizni tanlang:",
        "choose_tutor": "👨‍🏫 Tyutorni tanlang:",
        "write_question": "✍️ Savolingizni yozing:",
        "sent": "✔ Savolingiz tyutorlarga yuborildi!\n⏳ Tez orada javob beramiz.",
        "again_prompt": "➕ Yana savol bermoqchimisiz?",
        "again_btn": "➕ Yana savol berish",
        "invalid_phone": "❗ Telefon raqamini to‘g‘ri kiriting.",
        "phone_ok": "✅ Raqam qabul qilindi.",
        "media_from_tutor": "🔊 Tyutordan media xabar yuborildi.",
        "btn_share": "📱 Raqamni ulashish",
        # Guruhga boradigan matnlar
        "group_new": "Yangi savol!",
        "group_student": "Talaba",
        "group_phone": "Telefon",
        "group_faculty": "Fakulteti",
        "group_tutor": "Tyutor",
        "group_question": "Savol",
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "lang_chosen": "Язык выбран: 🇷🇺 Русский",
        "share_phone": "📱 Отправьте номер телефона или введите вручную:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите ваш вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьюторам!\n⏳ Скоро получите ответ.",
        "again_prompt": "➕ Хотите задать ещё вопрос?",
        "again_btn": "➕ Задать ещё вопрос",
        "invalid_phone": "❗ Введите корректный номер телефона.",
        "phone_ok": "✅ Номер принят.",
        "media_from_tutor": "🔊 От тьютора получено медиа-сообщение.",
        "btn_share": "📱 Поделиться номером",
        "group_new": "Новый вопрос!",
        "group_student": "Студент",
        "group_phone": "Телефон",
        "group_faculty": "Факультет",
        "group_tutor": "Тьютор",
        "group_question": "Вопрос",
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "lang_chosen": "Language selected: 🇬🇧 English",
        "share_phone": "📱 Please share your phone number or type it manually:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select a tutor:",
        "write_question": "✍️ Type your question:",
        "sent": "✔ Your question was sent to tutors.\n⏳ You’ll get a reply soon.",
        "again_prompt": "➕ Would you like to ask another question?",
        "again_btn": "➕ Ask another question",
        "invalid_phone": "❗ Please enter a valid phone number.",
        "phone_ok": "✅ Phone number saved.",
        "media_from_tutor": "🔊 A media message was sent by the tutor.",
        "btn_share": "📱 Share phone number",
        "group_new": "New question!",
        "group_student": "Student",
        "group_phone": "Phone",
        "group_faculty": "Faculty",
        "group_tutor": "Tutor",
        "group_question": "Question",
    },
}

# =======================
# FAKULTETLAR + TYUTORLAR (lotincha F.I.Sh.)
# =======================
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tutors": [
            {"name": "Khursandova Dilafruz", "id": 6939098356},
        ],
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "ru": "Экология и право",
        "en": "Ecology and Law",
        "tutors": [
                {"name": "Ahmedova Iroda", "id": 6926132637},
                {"name": "Shonazarov Akbar", "id": 2052678760},
                {"name": "Saidova Khursanoy", "id": 702931087},
                {"name": "Khudoynazarova Dilnavoz", "id": 310033808},
        ],
    },
    "mech": {
        "uz": "Qishloq xo‘jaligini mexanizatsiyalash",
        "ru": "Механизация сельского хозяйства",
        "en": "Agricultural Mechanization",
        "tutors": [],
    },
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tutors": [
            {"name": "Abdullaev Botir", "id": 485351327},
        ],
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "ru": "Земельные ресурсы и кадастр",
        "en": "Land Resources and Cadastre",
        "tutors": [
            {"name": "Turgunova Maftuna", "id": 8376601534},
            {"name": "Abdullaeva Oliya", "id": 2134838705},
        ],
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tutors": [
            {"name": "Ahmedjanova Gulchehra", "id": 503802473},
        ],
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tutors": [
            {"name": "Egamova Dilbar", "id": 115619153},
            {"name": "Shodieva Gulbahor", "id": 401016810},
        ],
    },
}

# mapping (fallback sifatida ID satridagi raqamdan ham foydalanamiz)
pending_questions: dict[int, dict] = {}

# =======================
# Helperlar
# =======================
def make_lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
    ])

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
    await update.message.reply_text(LANG_PACK["uz"]["start"], reply_markup=make_lang_keyboard())

# =======================
# Til tanlash
# =======================
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, lang = q.data.split("|")
    if lang not in LANG_PACK:
        lang = "uz"
    context.user_data["lang"] = lang
    context.user_data["state"] = "await_phone"
    t = LANG_PACK[lang]
    await q.edit_message_text(t["lang_chosen"])
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(t["btn_share"], request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    await q.message.reply_text(t["share_phone"], reply_markup=kb)

# =======================
# Private chat — text/contact
# =======================
async def handle_private(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return
    msg = update.message
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]
    state = context.user_data.get("state")

    # Contact kelsa — doimo qabul qilamiz
    if msg.contact:
        context.user_data["phone"] = msg.contact.phone_number
        context.user_data["state"] = "await_faculty"
        await msg.reply_text(t["phone_ok"], reply_markup=ReplyKeyboardRemove())
        await msg.reply_text(t["choose_faculty"], reply_markup=make_faculty_keyboard(lang))
        return

    if not msg.text:
        return

    # Qo‘lda kiritilgan telefon
    if state == "await_phone":
        phone = msg.text.strip()
        clean = phone.replace("+", "").replace(" ", "").replace("-", "")
        if not clean.isdigit() or len(clean) < 7:
            await msg.reply_text(t["invalid_phone"])
            return
        context.user_data["phone"] = phone
        context.user_data["state"] = "await_faculty"
        await msg.reply_text(t["phone_ok"], reply_markup=ReplyKeyboardRemove())
        await msg.reply_text(t["choose_faculty"], reply_markup=make_faculty_keyboard(lang))
        return

    # Savol yozish bosqichi
    if state == "await_question":
        await handle_student_question(update, context)
        return
    # Boshqa holatlarda jim.

# =======================
# Fakultet tanlash
# =======================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    _, fac_key = q.data.split("|")
    if fac_key not in FACULTIES:
        return
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]
    context.user_data["faculty_key"] = fac_key
    context.user_data["faculty_name"] = FACULTIES[fac_key][lang]
    tutors = FACULTIES[fac_key]["tutors"]

    if not tutors:
        context.user_data["selected_tutor_id"] = None
        context.user_data["selected_tutor_name"] = "Tyutor (biriktirilmagan)" if lang == "uz" else \
                                                   ("Тьютор не назначен" if lang == "ru" else "Tutor (not assigned)")
        context.user_data["state"] = "await_question"
        await q.edit_message_text(t["write_question"])
        return

    kb = [[InlineKeyboardButton(tu["name"], callback_data=f"tutor|{fac_key}|{tu['id']}")] for tu in tutors]
    context.user_data["state"] = "await_tutor"
    await q.edit_message_text(t["choose_tutor"], reply_markup=InlineKeyboardMarkup(kb))

# =======================
# Tyutor tanlash
# =======================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    try:
        _, fac_key, tutor_id = q.data.split("|")
        tutor_id = int(tutor_id)
    except Exception:
        return
    if fac_key not in FACULTIES:
        return
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]
    context.user_data["faculty_name"] = FACULTIES[fac_key][lang]
    tutor_name = next((tu["name"] for tu in FACULTIES[fac_key]["tutors"] if tu["id"] == tutor_id), None)
    if tutor_name is None:
        return
    context.user_data["selected_tutor_id"] = tutor_id
    context.user_data["selected_tutor_name"] = tutor_name
    context.user_data["state"] = "await_question"
    await q.edit_message_text(t["write_question"])

# =======================
# Savolni guruhga yuborish
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

    # Talaba clickable (faqat guruhda)
    full_name = (user.first_name or "") + (f" {user.last_name}" if user.last_name else "")
    student_mention = f'<a href="tg://user?id={user.id}">{html.escape(full_name.strip() or "Student")}</a>'
    username_part = f" (@{user.username})" if user.username else ""
    tutor_label = html.escape(tutor_name) if not tutor_id else f'<a href="tg://user?id={tutor_id}">{html.escape(tutor_name)}</a>'

    text = (
        f"📩 <b>{t['group_new']}</b>\n\n"
        f"👤 {t['group_student']}: {student_mention}{html.escape(username_part)}\n"
        f"🆔 ID: {user.id}\n"
        f"📞 {t['group_phone']}: {html.escape(phone)}\n"
        f"🏫 {t['group_faculty']}: {html.escape(faculty_name)}\n"
        f"👨‍🏫 {t['group_tutor']}: {tutor_label}\n\n"
        f"💬 {t['group_question']}:\n<blockquote>{html.escape(question)}</blockquote>"
    )

    sent = await context.bot.send_message(
        TUTORS_GROUP_ID, text, parse_mode="HTML", disable_web_page_preview=True
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
    if not msg or not msg.reply_to_message:
        return

    original = msg.reply_to_message
    info = pending_questions.get(original.message_id)
    user_id, lang = (info.get("user_id"), info.get("lang", "uz")) if info else (None, "uz")

    if user_id is None:
        source = original.text or ""
        m = ID_RE.search(source)
        if m:
            try:
                user_id = int(m.group(1))
            except ValueError:
                user_id = None
    if user_id is None:
        return

    t = LANG_PACK.get(lang, LANG_PACK["uz"])
    # Faqat ism-familiya (username/link/ID yo‘q)
    tutor_name = (msg.from_user.first_name or "")
    if msg.from_user.last_name:
        tutor_name += f" {msg.from_user.last_name}"

    answer_text = msg.text or msg.caption or t["media_from_tutor"]

    try:
        await context.bot.send_message(user_id, f"👨‍🏫 {tutor_name}:\n\n{answer_text}")
        await context.bot.send_message(
            user_id,
            t["again_prompt"],
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(t["again_btn"], callback_data="again")]])
        )
    except Exception as e:
        logger.error("Talabaga javob yuborishda xato: %s", e)
        return

    pending_questions.pop(original.message_id, None)

# =======================
# "Yana savol berish"
# =======================
async def ask_again(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]
    context.user_data["state"] = "await_faculty"
    await q.message.reply_text(t["choose_faculty"], reply_markup=make_faculty_keyboard(lang))

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

    # Private chat: barcha text/contact shu handlerga tushadi
    app.add_handler(MessageHandler(filters.ChatType.PRIVATE & ~filters.COMMAND, handle_private))

    # Guruhdagi tyutor javoblari
    app.add_handler(MessageHandler(filters.Chat(TUTORS_GROUP_ID) & ~filters.COMMAND & ~filters.StatusUpdate.ALL, tutor_group_reply))

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
