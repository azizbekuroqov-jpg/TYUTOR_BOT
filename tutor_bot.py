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
import datetime

# =======================
# CONFIG
# =======================

BOT_TOKEN = "YOUR_TELEGRAM_TOKEN"
ADMIN_ID = 8012275825
TUTORS_GROUP_ID = -4838121362

# =======================================
# 4 TA TIL UCHUN MATNLAR
# =======================================

LANG_PACK = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing:",
        "choose_faculty": "Fakultetingizni tanlang:",
        "choose_tutor": "Tyutorni tanlang:",
        "write_question": "Savolingizni yozing:",
        "sent_to_group": "Savolingiz tyutorlarga yuborildi! ✔",
        "new_student": "📱 *Yangi talaba ro’yxatdan o‘tdi!*",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте свой номер телефона:",
        "choose_faculty": "Выберите факультет:",
        "choose_tutor": "Выберите тьютора:",
        "write_question": "Введите ваш вопрос:",
        "sent_to_group": "Ваш вопрос отправлен тьюторам! ✔",
        "new_student": "📱 *Зарегистрирован новый студент!*",
    },
    "en": {
        "choose_lang": "Choose language:",
        "share_phone": "📱 Please share your phone number:",
        "choose_faculty": "Select your faculty:",
        "choose_tutor": "Select tutor:",
        "write_question": "Write your question:",
        "sent_to_group": "Your question has been sent to tutors! ✔",
        "new_student": "📱 *A new student has registered!*",
    },
    "tm": {
        "choose_lang": "Dili saýlaň:",
        "share_phone": "📱 Telefon belginizi paýlaşyň:",
        "choose_faculty": "Fakulteti saýlaň:",
        "choose_tutor": "Tyutory saýlaň:",
        "write_question": "Soragyňyzy ýazyň:",
        "sent_to_group": "Soragyňyz ugradyldy! ✔",
        "new_student": "📱 *Täze talyp registrasiýa edildi!*",
    }
}

# =======================================
# FAKULTET NOMLARI 4 TILDA
# =======================================

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
        "uz": "Mexanizatsiya",
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
            {"name": "Эгамова Дилbar", "id": 115619153},
            {"name": "Шодиева Гулbahor", "id": 401016810},
        ]
    }
}

# Barcha tyutorlar — guruh xabari uchun
ALL_TUTORS = []
for f in FACULTIES.values():
    ALL_TUTORS += f["tutors"]

pending_questions = {}


# =======================
# /start → TIL TANLASH
# =======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]
    await update.message.reply_text("Tilni tanlang:", reply_markup=InlineKeyboardMarkup(keyboard))


# =======================
# TIL TANLANGANDA → TELEFON SO‘RALADI
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


# =======================
# TELEFON KELGANDA → GURUHGA YUBORILADI
# =======================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone

    lang = context.user_data["lang"]
    text = LANG_PACK[lang]

    await context.bot.send_message(
        TUTORS_GROUP_ID,
        f"{text['new_student']}\n"
        f"👤 [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}",
        parse_mode="Markdown"
    )

    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        text["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
# FAKULTET TANLANGANDA
# =======================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, key = query.data.split("|")
    lang = context.user_data["lang"]

    tutors = FACULTIES[key]["tutors"]

    if len(tutors) == 0:
        context.user_data["faculty"] = FACULTIES[key][lang]
        await query.edit_message_text("Savolingizni yozing:")
        return

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{key}|{t['id']}")]
        for t in tutors
    ]

    await query.edit_message_text(
        LANG_PACK[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================
# TUTOR TANLANGANDA
# =======================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key, tutor_id = query.data.split("|")
    tutor_id = int(tutor_id)

    lang = context.user_data["lang"]

    tutor_name = ""
    for t in FACULTIES[fac_key]["tutors"]:
        if t["id"] == tutor_id:
            tutor_name = t["name"]

    context.user_data["faculty"] = FACULTIES[fac_key][lang]
    context.user_data["selected_tutor"] = tutor_id
    context.user_data["selected_tutor_name"] = tutor_name

    await query.edit_message_text(LANG_PACK[lang]["write_question"])


# =======================
# SAVOL — GURUHGA tg://user?id=ID bilan ATMETKA qilinadi
# =======================
async def send_question_to_group(context, user, phone, faculty, tutor_id, tutor_name, question):

    mention = f"[{tutor_name}](tg://user?id={tutor_id})"

    msg = (
        "📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 Telefon: {phone}\n"
        f"🏫 Fakultet: {faculty}\n\n"
        f"👨‍🏫 *Tyutor:* {mention}  ← chaqirildi!\n\n"
        f"💬 *Savol:* {question}"
    )

    await context.bot.send_message(TUTORS_GROUP_ID, msg, parse_mode="Markdown")


# =======================
# SAVOL QABUL QILINGANDA
# =======================
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    question = update.message.text

    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id = context.user_data["selected_tutor"]
    tutor_name = context.user_data["selected_tutor_name"]

    # Guruhga yuboramiz
    await send_question_to_group(context, user, phone, faculty, tutor_id, tutor_name, question)

    await update.message.reply_text(LANG_PACK[context.user_data["lang"]]["sent_to_group"])


# =======================
# TUTOR JAVOB BERGANDA → TALABAGA BORADI
# =======================
async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutor = update.message.from_user
    msg = update.message.text

    for qid, data in pending_questions.items():
        if data["tutor_id"] == tutor.id and not data["answered"]:
            await context.bot.send_message(data["user_id"], f"📨 Tyutordan javob:\n{msg}")
            data["answered"] = True
            break


# =======================
# BOTNI ISHGA TUSHIRISH
# =======================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    app.add_handler(MessageHandler(filters.TEXT, tutor_reply))

    app.run_polling()


if __name__ == "__main__":
    main()
