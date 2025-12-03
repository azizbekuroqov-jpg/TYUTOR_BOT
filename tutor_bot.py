import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes
)
import datetime

# =======================================
# CONFIG — BU YERNI SOZLANG
# =======================================

BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
ADMIN_ID = 8012275825
TUTORS_GROUP_ID = -4838121362


# =======================================
# 4 TA TIL UCHUN MATNLAR
# =======================================

LANG_PACK = {
    "uz": {
        "choose_lang": "Tilni tanlang:",
        "choose_faculty": "Fakultetingizni tanlang:",
        "choose_tutor": "Tyutorni tanlang:",
        "write_question": "Savolingizni yozing:",
        "sent_to_tutor": "Savol tyutorga yuborildi! ✔",
        "no_tutor": "Bu fakultetda tyutor yo‘q. Savolingizni yozing:",
        "new_question": "Sizga yangi savol!",
        "remind_3h": "⏳ 3 soat bo‘ldi — javob berilmadi.",
        "remind_12h": "⚡ 12 soat bo‘ldi — javob berilmadi.",
        "report_24h": "❗ Tyutor 24 soat davomida javob bermadi.",
    },
    "ru": {
        "choose_lang": "Выберите язык:",
        "choose_faculty": "Выберите факультет:",
        "choose_tutor": "Выберите тьютора:",
        "write_question": "Введите ваш вопрос:",
        "sent_to_tutor": "Вопрос отправлен тьютору! ✔",
        "no_tutor": "Для этого факультета нет тьютора. Напишите ваш вопрос:",
        "new_question": "Вам поступил новый вопрос!",
        "remind_3h": "⏳ Прошло 3 часа — нет ответа.",
        "remind_12h": "⚡ Прошло 12 часов — нет ответа.",
        "report_24h": "❗ Тьютор не ответил 24 часа.",
    },
    "en": {
        "choose_lang": "Choose your language:",
        "choose_faculty": "Select your faculty:",
        "choose_tutor": "Select a tutor:",
        "write_question": "Type your question:",
        "sent_to_tutor": "Your question was sent to the tutor! ✔",
        "no_tutor": "No tutor for this faculty. Type your question:",
        "new_question": "You have a new question!",
        "remind_3h": "⏳ 3 hours passed — no reply.",
        "remind_12h": "⚡ 12 hours passed — no reply.",
        "report_24h": "❗ The tutor didn't reply for 24 hours.",
    },
    "tm": {
        "choose_lang": "Dili saýlaň:",
        "choose_faculty": "Fakulteti saýlaň:",
        "choose_tutor": "Tyutory saýlaň:",
        "write_question": "Soragyňyzy ýazyň:",
        "sent_to_tutor": "Sorag tyutora iberildi! ✔",
        "no_tutor": "Bu fakultetde tyutor ýok. Soragyňyzy ýazyň:",
        "new_question": "Siziň täze soraňyz bar!",
        "remind_3h": "⏳ 3 sagat geçdi — jogap ýok.",
        "remind_12h": "⚡ 12 sagat geçdi — jogap ýok.",
        "report_24h": "❗ Tyutor 24 sagat jogap bermedi.",
    }
}


# =======================================
# FAKULTET TARJIMALARI (4 til)
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
            {"name": "Эгамова Дилбар", "id": 115619153},
            {"name": "Шодиева Гулбахор", "id": 401016810},
        ]
    }
}

pending_questions = {}


# =======================================
# /start — TIL TANLASH
# =======================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O‘zbek", callback_data="lang|uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang|ru")],
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang|en")],
        [InlineKeyboardButton("🇹🇲 Türkmençe", callback_data="lang|tm")],
    ]

    await update.message.reply_text(
        "Tilni tanlang / Choose language:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================================
# TIL TANLANGANDA
# =======================================

async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data.split("|")[1]
    context.user_data["lang"] = lang
    text = LANG_PACK[lang]

    # Fakultetlarni 4 tilda chiqarish
    keyboard = []
    for key, fac in FACULTIES.items():
        keyboard.append([InlineKeyboardButton(fac[lang], callback_data=f"faculty|{key}")])

    await query.edit_message_text(
        text["choose_faculty"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================================
# FAKULTET TANLANGANDA
# =======================================

async def faculty_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key = query.data.split("|")
    lang = context.user_data["lang"]
    text = LANG_PACK[lang]

    faculty = FACULTIES[fac_key]
    tutors = faculty["tutors"]

    # Tyutor yo‘q bo‘lsa
    if len(tutors) == 0:
        await query.edit_message_text(text["no_tutor"])
        context.user_data["direct_to_group"] = True
        context.user_data["faculty"] = faculty[lang]
        return

    # Tyutorlarni chiqarish
    keyboard = [
        [InlineKeyboardButton(t["name"], callback_data=f"tutor|{fac_key}|{t['id']}")]
        for t in tutors
    ]

    await query.edit_message_text(
        text["choose_tutor"],
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# =======================================
# TUTOR TANLANGANDA
# =======================================

async def tutor_selected(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    _, fac_key, tutor_id = query.data.split("|")
    tutor_id = int(tutor_id)

    context.user_data["selected_tutor"] = tutor_id
    context.user_data["faculty"] = FACULTIES[fac_key][context.user_data["lang"]]

    lang = context.user_data["lang"]
    text = LANG_PACK[lang]

    await query.edit_message_text(text["write_question"])


# =======================================
# TALABA SAVOL YOZGANDA
# =======================================

async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text_msg = update.message.text

    lang = context.user_data["lang"]
    text = LANG_PACK[lang]

    faculty = context.user_data.get("faculty")
    tutor_id = context.user_data.get("selected_tutor")
    direct_group = context.user_data.get("direct_to_group", False)

    timestamp = datetime.datetime.now()
    qid = f"{user.id}_{timestamp.timestamp()}"

    pending_questions[qid] = {
        "user_id": user.id,
        "faculty": faculty,
        "question": text_msg,
        "tutor_id": tutor_id,
        "answered": False,
        "time": timestamp
    }

    # Tyutor yo‘q → guruhga yuborish
    if direct_group:
        await context.bot.send_message(
            TUTORS_GROUP_ID,
            f"❗ {faculty}\n"
            f"👤 [{user.first_name}](tg://user?id={user.id})\n"
            f"💬 {text_msg}",
            parse_mode="Markdown"
        )
        return

    # Tyutor ga yuborish
    await context.bot.send_message(
        tutor_id,
        f"📩 {LANG_PACK[lang]['new_question']}\n"
        f"👤 [{user.first_name}](tg://user?id={user.id})\n"
        f"🏫 {faculty}\n"
        f"💬 {text_msg}",
        parse_mode="Markdown"
    )

    await update.message.reply_text(text["sent_to_tutor"])


# =======================================
# TUTOR JAVOB BERGANDA
# =======================================

async def tutor_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tutor = update.message.from_user
    msg = update.message.text

    for qid, data in pending_questions.items():
        if data["tutor_id"] == tutor.id and not data["answered"]:

            await context.bot.send_message(
                data["user_id"],
                f"📨 {msg}"
            )

            data["answered"] = True
            break


# =======================================
# 3 / 12 / 24 SOAT MONITORING
# =======================================

async def monitor(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now()

    for qid, data in pending_questions.items():
        if data["answered"]:
            continue

        diff = now - data["time"]
        hours = diff.total_seconds() / 3600

        tutor_id = data["tutor_id"]
        faculty = data["faculty"]
        lang = "uz"

        # Default til
        if "lang" in data:
            lang = data["lang"]

        pack = LANG_PACK["uz"]

        if 3 <= hours < 3.1:
            await context.bot.send_message(tutor_id, pack["remind_3h"])

        if 12 <= hours < 12.1:
            await context.bot.send_message(tutor_id, pack["remind_12h"])

        if 24 <= hours < 24.1:
            await context.bot.send_message(
                TUTORS_GROUP_ID,
                f"❗ {faculty}\n"
                f"{pack['report_24h']}\n"
                f"💬 {data['question']}"
            )


# =======================================
# BOTNI ISHGA TUSHIRISH
# =======================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(choose_language, pattern="lang"))
    app.add_handler(CallbackQueryHandler(faculty_selected, pattern="faculty"))
    app.add_handler(CallbackQueryHandler(tutor_selected, pattern="tutor"))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    app.add_handler(MessageHandler(filters.TEXT, tutor_reply))

    app.job_queue.run_repeating(monitor, interval=600)

    app.run_polling()


if __name__ == "__main__":
    main()
