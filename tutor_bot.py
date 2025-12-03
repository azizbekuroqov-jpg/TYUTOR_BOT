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

BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
TUTORS_GROUP_ID = -1003374172310

LANG = {
    "uz": {
        "hello": "Assalomu alaykum! 😊\nTilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing:",
        "choose_faculty": "🏫 Fakultetingizni tanlang:",
        "choose_tutor": "👨‍🏫 Tyutorni tanlang:",
        "write_question": "✍️ Savolingizni yozing:",
        "sent_to_group": "✔️ Savolingiz yuborildi! Tez orada javob beramiz.",
        "new_student": "📱 *Yangi talaba ro’yxatdan o‘tdi!*"
    },
    "ru": {
        "hello": "Здравствуйте! 😊\nВыберите язык:",
        "share_phone": "📱 Пожалуйста, отправьте ваш номер:",
        "choose_faculty": "🏫 Выберите факультет:",
        "choose_tutor": "👨‍🏫 Выберите тьютора:",
        "write_question": "✍️ Введите ваш вопрос:",
        "sent_to_group": "✔️ Ваш вопрос отправлен!",
        "new_student": "📱 *Новый студент зарегистрирован!*"
    },
    "en": {
        "hello": "Hello! 😊\nChoose language:",
        "share_phone": "📱 Please share your phone number:",
        "choose_faculty": "🏫 Select your faculty:",
        "choose_tutor": "👨‍🏫 Select tutor:",
        "write_question": "✍️ Write your question:",
        "sent_to_group": "✔️ Your question has been sent!",
        "new_student": "📱 *New student registered!*"
    },
    "tm": {
        "hello": "Salam! 😊\nDili saýlaň:",
        "share_phone": "📱 Telefon belginizi paýlaşyň:",
        "choose_faculty": "🏫 Fakulteti saýlaň:",
        "choose_tutor": "👨‍🏫 Mugallymy saýlaň:",
        "write_question": "✍️ Soragyny ýaz:",
        "sent_to_group": "✔️ Sorag ugradyldy!",
        "new_student": "📱 *Täze talyp goşuldy!*"
    }
}

# Fakultetlar
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "ru": "Гидротехническое строительство",
        "en": "Hydraulic Engineering",
        "tm": "Gidrotehniki gurluşyk",
        "tutors": [{"name": "Хурсандова Дилафруз", "id": 6939098356}]
    },
    "eco": {
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
    "energy": {
        "uz": "Energetika",
        "ru": "Энергетика",
        "en": "Energy Engineering",
        "tm": "Energetika",
        "tutors": [{"name": "Абдуллаев Ботир", "id": 841780299}]
    }
}

# ==========================
# START
# ==========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]

    await update.message.reply_text(
        "Assalomu alaykum! 😊\nTilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================
# LANGUAGE SELECTED
# ==========================
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    lang = q.data.split("|")[1]
    context.user_data["lang"] = lang

    # faqat 1 marta yuboriladi!
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

    await q.edit_message_text(LANG[lang]["share_phone"])
    await q.message.reply_text(LANG[lang]["share_phone"], reply_markup=kb)

# ==========================
# CONTACT RECEIVED
# ==========================
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    phone = update.message.contact.phone_number
    lang = context.user_data["lang"]

    context.user_data["phone"] = phone

    # Keyboardni yopish
    await update.message.reply_text("✔ Raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())

    # ——— fakultetlar menyusi ———
    keyboard = [
        [InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")]
        for key, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG[lang]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

    # ❗ GURUHGA FAQAT 1 MARTA XABAR!
    await context.bot.send_message(
        TUTORS_GROUP_ID,
        f"{LANG[lang]['new_student']}\n"
        f"👤 [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}",
        parse_mode="Markdown"
    )


# ==========================
# FACULTY SELECTED
# ==========================
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    lang = context.user_data["lang"]
    fac_key = q.data.split("|")[1]

    context.user_data["faculty"] = FACULTIES[fac_key][lang]

    tutors = FACULTIES[fac_key]["tutors"]

    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{t['id']}|{t['name']}")]
        for t in tutors
    ]

    await q.edit_message_text(
        LANG[lang]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ==========================
# TUTOR SELECTED
# ==========================
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):

    q = update.callback_query
    await q.answer()

    _, tutor_id, tutor_name = q.data.split("|")

    context.user_data["tutor_id"] = int(tutor_id)
    context.user_data["tutor_name"] = tutor_name
    context.user_data["step"] = "ask"

    lang = context.user_data["lang"]
    await q.edit_message_text(LANG[lang]["write_question"])

# ==========================
# QUESTION HANDLING
# ==========================
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("step") != "ask":
        return

    user = update.message.from_user
    question = update.message.text

    lang = context.user_data["lang"]
    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id = context.user_data["tutor_id"]
    tutor_name = context.user_data["tutor_name"]

    # Talabaga xabar
    await update.message.reply_text(LANG[lang]["sent_to_group"])

    # Guruhga xabar
    await context.bot.send_message(
        TUTORS_GROUP_ID,
        f"📩 *Yangi savol!*\n"
        f"👤 [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 {phone}\n"
        f"🏫 {faculty}\n"
        f"👨‍🏫 [{tutor_name}](tg://user?id={tutor_id})\n\n"
        f"💬 *Savол:* {question}",
        parse_mode="Markdown"
    )

    context.user_data["step"] = None

# ==========================
# MAIN
# ==========================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    app.run_polling()


if __name__ == "__main__":
    main()
