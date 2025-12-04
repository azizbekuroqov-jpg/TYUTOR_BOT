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

BOT_TOKEN = "8368341342:AAEI1mEI17zWjOJYPogINydMQEIKE1XDLcE"      # <-- O'Z BOT TOKENINGIZNI YOZING
TUTORS_GROUP_ID = -1003374172310       # <-- TYUTORLAR GURUHI ID

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
        "invalid_phone": "❗ Telefon raqamini to‘g‘ri kiriting.",
        "phone_ok": "✅ Raqam qabul qilindi.",
        "again_button": "➕ Yana savol berish",
    },
    "ru": {
        "start": "Здравствуйте!\nВыберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте свой номер или введите вручную:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Напишите ваш вопрос:",
        "sent": "✔ Ваш вопрос отправлен тьюторам!\n⏳ Скоро получите ответ.",
        "again": "➕ Хотите задать ещё вопрос?",
        "invalid_phone": "❗ Введите корректный номер телефона.",
        "phone_ok": "✅ Номер принят.",
        "again_button": "➕ Задать ещё вопрос",
    },
    "en": {
        "start": "Hello!\nChoose language:",
        "share_phone": "📱 Please share your phone number or type it manually:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select tutor:",
        "write_question": "✍️ Write your question:",
        "sent": "✔ Your question has been sent!\n⏳ Tutors will reply soon.",
        "again": "➕ Do you want to ask another question?",
        "invalid_phone": "❗ Please enter a valid phone number.",
        "phone_ok": "✅ Phone number saved.",
        "again_button": "➕ Ask another question",
    },
    "tm": {
        "start": "Salam!\nDili saýlaň:",
        "share_phone": "📱 Telefon belgiňiz paýlaşyň ýa-da el bilen ýazyň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Tyutory saýlaň:",
        "write_question": "✍️ Soragyňyzy ýazyň:",
        "sent": "✔ Soragyňyz ugradyldy!\n⏳ Jogap gysga wagtda gelýär.",
        "again": "➕ Ýene-de sorag bermek isleýärsiňizmi?",
        "invalid_phone": "❗ Telefon belgiňiz dogry däl.",
        "phone_ok": "✅ Telefon belgiňiz kabul edildi.",
        "again_button": "➕ Ýene sorag bermek",
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
            {"name": "Худойназарova Дилнавoz", "id": 310033808},
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
            {"name": "Турғунova Мафтуна", "id": 8376601534},
            {"name": "Абдулlaeva Oliyа", "id": 2134838705},
        ],
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "ru": "Гидромелиорация",
        "en": "Hydromelioration",
        "tm": "Gidromeliorasiýa",
        "tutors": [
            {"name": "Ахмеджanova Гулчеҳra", "id": 503802473},
        ],
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "ru": "Экономика",
        "en": "Economics",
        "tm": "Ykdysadyýet",
        "tutors": [
            {"name": "Эгамова Дильbar", "id": 115619153},
            {"name": "Шодиеva Gулbahor", "id": 401016810},
        ],
    },
}

# Guruhdagi savol xabari ID → {"user_id": ..., "lang": ...}
pending_questions: dict[int, dict] = {}


# =======================
# YORDAMCHI FUNKSIYALAR
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
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
            for key, fac in FACULTIES.items()
        ]
    )


# =======================
# /start
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Har safar /start — holatni tozalaymiz
    context.user_data.clear()
    context.user_data["state"] = "await_lang"

    await update.message.reply_text(
        "Assalomu alaykum!\nTilni tanlang:",
        reply_markup=make_lang_keyboard(),
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

    t = LANG_PACK[lang]

    # Telefon tugmasi faqat shu yerda chiqadi
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

    # Eski xabarni til tanlangan matnga o‘zgartiramiz
    await query.edit_message_text(t["start"])
    # Yangi xabar — telefon so‘rash
    await query.message.reply_text(t["share_phone"], reply_markup=kb)


# =======================
# Telefon (contact) – faqat PHONE bosqichida
# =======================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("state") != "await_phone":
        return

    lang = context.user_data.get("lang", "uz")
    t = LANG_PACK[lang]

    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone
    context.user_data["state"] = "await_faculty"

    # Bitta xabar ichida ham tasdiq, ham fakultet menyusi
    msg = f"{t['phone_ok']}\n\n{t['choose_faculty']}"

    await update.message.reply_text(
        msg,
        reply_markup=make_faculty_keyboard(lang),
        reply_markup_remove=ReplyKeyboardRemove()  # bu parametr yo'q, ReplyKeyboardRemove alohida
    )
