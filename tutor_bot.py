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

# === CONFIG ===
BOT_TOKEN = "8368341342:AAF-QsZxrdrgrzlppQZpJke9C8tdXNo_VOE"
TUTORS_GROUP_ID = -1003374172310
ADMIN_ID = 8012275825

# === LANG PACK ===
LANG = {
    "uz": {
        "hello": "Assalomu alaykum! 😊",
        "choose_lang": "Tilni tanlang:",
        "share_phone": "📱 Iltimos, telefon raqamingizni ulashing:",
        "choose_faculty": "Fakultetingizni tanlang:",
        "choose_tutor": "Tyutorni tanlang:",
        "write_question": "Savolingizni yozing:",
        "sent_to_group": "Murojaatingiz uchun rahmat! Tez orada sizga javob beramiz. 😊",
        "new_student": "📱 *Yangi talaba ro‘yhatdan o‘tdi!*"
    }
}

# === FACULTIES ===
FACULTIES = {
    "hydraulic": {
        "uz": "Gidrotexnika qurilishi",
        "tutors": [
            {"name": "Хурсандова Дилафруз", "id": 6939098356}
        ]
    },
    "eco_law": {
        "uz": "Ekologiya va huquq",
        "tutors": [
            {"name": "Ахмедова Ирода", "id": 6926132637},
            {"name": "Шоназаров Акбар", "id": 2052678760},
            {"name": "Саидова Хурсаной", "id": 702931087},
            {"name": "Худойназарова Дилнавоз", "id": 310033808}
        ]
    },
    "mech": {"uz": "Mexanizatsiya", "tutors": []},
    "energy": {
        "uz": "Energetika",
        "tutors": [{"name": "Абдуллаев Ботир", "id": 485351327}]
    },
    "land": {
        "uz": "Yer resurslari va kadastr",
        "tutors": [
            {"name": "Турғунова Мафтуна", "id": 8376601534},
            {"name": "Абдуллаева Олия", "id": 2134838705}
        ]
    },
    "hydromel": {
        "uz": "Gidromelioratsiya",
        "tutors": [{"name": "Ахмеджанова Гулчеҳра", "id": 503802473}]
    },
    "economy": {
        "uz": "Iqtisodiyot",
        "tutors": [
            {"name": "Эгамова Дилbar", "id": 115619153},
            {"name": "Шодиева Гулbahor", "id": 401016810}
        ]
    }
}

# === START ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Assalomu alaykum! 😊")

    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang_uz")]
    ]

    await update.message.reply_text(
        "Tilni tanlang:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# === LANGUAGE SELECT ===
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    context.user_data["lang"] = "uz"

    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 Raqamni ulashish", request_contact=True)]],
        resize_keyboard=True
    )

    await q.edit_message_text(LANG["uz"]["share_phone"])
    await q.message.reply_text(LANG["uz"]["share_phone"], reply_markup=kb)


# === CONTACT HANDLING ===
async def handle_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user
    phone = update.message.contact.phone_number
    context.user_data["phone"] = phone

    # Hide keyboard
    await update.message.reply_text("✔ Raqam qabul qilindi", reply_markup=ReplyKeyboardRemove())

    # Fakultetlar
    kb = [
        [InlineKeyboardButton(fac["uz"], callback_data=f"faculty|{k}")]
        for k, fac in FACULTIES.items()
    ]

    await update.message.reply_text(
        LANG["uz"]["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(kb)
    )

    # Send to group
    try:
        await context.bot.send_message(
            TUTORS_GROUP_ID,
            f"{LANG['uz']['new_student']}\n"
            f"👤 [{user.first_name}](tg://user?id={user.id})\n"
            f"📞 {phone}",
            parse_mode="Markdown"
        )
    except:
        pass


# === FACULTY SELECT ===
async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    key = q.data.split("|")[1]
    context.user_data["faculty"] = FACULTIES[key]["uz"]

    tutors = FACULTIES[key]["tutors"]

    if len(tutors) == 0:
        await q.edit_message_text("Savolingizni yozing:")
        context.user_data["step"] = "ask"
        return

    kb = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{key}|{t['id']}")]
        for t in tutors
    ]

    await q.edit_message_text(
        LANG["uz"]["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(kb)
    )


# === TUTOR SELECT ===
async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    _, fac_key, tutor_id = q.data.split("|")
    tutor_id = int(tutor_id)

    for t in FACULTIES[fac_key]["tutors"]:
        if t["id"] == tutor_id:
            context.user_data["tutor_name"] = t["name"]

    context.user_data["tutor_id"] = tutor_id
    context.user_data["step"] = "ask"

    await q.edit_message_text(LANG["uz"]["write_question"])


# === QUESTION HANDLING ===
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if context.user_data.get("step") != "ask":
        return

    user = update.message.from_user
    question = update.message.text

    phone = context.user_data["phone"]
    faculty = context.user_data["faculty"]
    tutor_id = context.user_data["tutor_id"]
    tutor_name = context.user_data["tutor_name"]

    # Studentga javob
    await update.message.reply_text(LANG["uz"]["sent_to_group"])

    # Guruhga yuborish
    msg = (
        "📩 *Yangi savol!*\n"
        f"👤 Talaba: [{user.first_name}](tg://user?id={user.id})\n"
        f"📞 Telefon: {phone}\n"
        f"🏫 Fakultet: {faculty}\n\n"
        f"👨‍🏫 Tyutor: [{tutor_name}](tg://user?id={tutor_id})\n\n"
        f"💬 *Savol:* {question}"
    )

    await context.bot.send_message(
        TUTORS_GROUP_ID, msg, parse_mode="Markdown"
    )

    context.user_data["step"] = None


# === MAIN ===
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang_uz"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.CONTACT, handle_contact))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))

    app.run_polling()

if __name__ == "__main__":
    main()
