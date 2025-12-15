import os
import json
import datetime
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = "YOURS"
ADMIN_ID = YourID
CHANNEL_ID = -100000000

DATA_FILE = "bot_data.json"
bot = Bot(BOT_TOKEN)

categories = ["Matematika", "Fizika", "Kimyo", "Biologiya", "Informatika", "Geografiya", "Tarix", "Adabiyot"]

# --- JSON HANDLERS ---
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {"users": {}}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

# --- TEMPORARY PENDING ---
pending_users = {}           # user_id -> {"subject": "Matematika"}
admin_pending_solution = {}  # admin_id -> (user_id, user_msg_id)

# --- START ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("📤 Masala yuborish", callback_data="masala_yuborish")]])
    await context.bot.send_message(
        chat_id,
        "👋 Assalomu alaykum!\n\n"
        "📚 Bu bot orqali siz fanlaringiz bo‘yicha masalalarni yuborishingiz va ularning yechimlarini olishingiz mumkin.\n\n"
        "✏️ Masala yuborish uchun pastdagi tugmani bosing 👇\n\n"
        "💡 Masalalarni yuborishda iloji boricha aniq va to‘liq yozing, rasm yoki fayl qo‘shishingiz mumkin.",
        reply_markup=kb
    )

# --- /MASALA COMMAND ---
async def masala(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    kb = []
    row = []
    for i, cat in enumerate(categories, 1):
        row.append(InlineKeyboardButton(cat, callback_data=f"subject_{cat}"))
        if i % 2 == 0:
            kb.append(row)
            row = []
    if row:
        kb.append(row)
    kb.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])
    await update.message.reply_text("📚 Fan tanlang:", reply_markup=InlineKeyboardMarkup(kb))

# --- CALLBACK HANDLER ---
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    chat_id = query.message.chat.id
    user_id = chat_id
    json_data = load_data()

    # --- USER: choose subject ---
    if data == "masala_yuborish":
        kb_buttons = []
        temp_row = []
        for i, cat in enumerate(categories, start=1):
            temp_row.append(InlineKeyboardButton(cat, callback_data=f"subject_{cat}"))
            if i % 2 == 0:
                kb_buttons.append(temp_row)
                temp_row = []
        if temp_row:
            kb_buttons.append(temp_row)
        kb_buttons.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])
        await bot.send_message(chat_id, "📚 Fanni tanlang:", reply_markup=InlineKeyboardMarkup(kb_buttons))
        await query.edit_message_reply_markup(None)
        return

    if data.startswith("subject_"):
        subject = data[8:]
        pending_users[user_id] = {"subject": subject}
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔙 Fan o‘zgartirish", callback_data="back_subject")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")]
        ])
        await bot.send_message(chat_id, f"✍️ {subject} bo‘yicha masalani yuboring (matn/rasm/fayl).", reply_markup=kb)
        await query.edit_message_reply_markup(None)
        return

    if data == "back_subject":
        kb = []
        row = []
        for i, cat in enumerate(categories, 1):
            row.append(InlineKeyboardButton(cat, callback_data=f"subject_{cat}"))
            if i % 2 == 0:
                kb.append(row)
                row = []
        if row:
            kb.append(row)
        kb.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])
        await bot.send_message(chat_id, "📚 Fan tanlang:", reply_markup=InlineKeyboardMarkup(kb))
        await query.edit_message_reply_markup(None)
        return

    if data == "cancel":
        pending_users.pop(user_id, None)
        await bot.send_message(chat_id, "❌ Masala yuborish bekor qilindi.")
        await query.edit_message_reply_markup(None)
        return

    # --- ADMIN: mark error / send solution ---
    if data.startswith("masala_error_"):
        parts = data.split("_")
        target_user_id = parts[-1]
        target_msg_id = parts[-2]
        problem = json_data["users"][target_user_id]["problems"][target_msg_id]
        problem["status"] = "error"
        save_data(json_data)
        await bot.send_message(int(target_user_id), f"❌ Masalada kamchilik bor. Fan: {problem['subject']}")
        await query.edit_message_reply_markup(None)
        return

    if data.startswith("send_solution_"):
        parts = data.split("_")
        target_user_id = parts[-1]
        target_msg_id = parts[-2]
        admin_pending_solution[ADMIN_ID] = (target_user_id, target_msg_id)
        problem = json_data["users"][target_user_id]["problems"][target_msg_id]
        await bot.send_message(ADMIN_ID, f"Masala uchun yechim kiriting (User ID: {target_user_id}, Fan: {problem['subject']})")
        await query.edit_message_reply_markup(None)
        return

    # --- RATING ---
    if data.startswith("rate_"):
        parts = data.split("_")
        score = int(parts[1])
        target_user_id = parts[2]
        target_msg_id = parts[3]
        # Notify user
        # 1️⃣ Reply to the solution message for the user
        await bot.send_message(
            chat_id=target_user_id,
            text=f"Rahmat! Siz {score}/10 ⭐️ baho berdingiz.",
            reply_to_message_id=int(target_msg_id)  # solution_msg_id = message ID sent to user
        )
        await query.delete_message()
        problem = json_data["users"][target_user_id]["problems"][target_msg_id]
        
        # 2️⃣ Notify admin with clickable link to storage channel
        channel_link = f"https://t.me/c/{str(CHANNEL_ID)[4:]}/{problem['channel_msg_id']}"
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"Foydalanuvchi ID {target_user_id} {score}/10 baho berdi.\n"
                f"Masala yechimi: [Ko‘rish]({channel_link})",
            parse_mode="Markdown"
        )
        await query.edit_message_reply_markup(None)
        return

# --- MESSAGE HANDLER ---
async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user_id = chat_id
    text = update.message.text or update.message.caption or ""
    photo = update.message.photo
    document = update.message.document
    json_data = load_data()

    # --- USER sends problem ---
    if user_id != ADMIN_ID and user_id in pending_users:
        subject = pending_users[user_id]["subject"]

        # Forward to storage channel
        if photo:
            storage_msg = await bot.send_photo(CHANNEL_ID, photo[-1].file_id,
                                               caption=f"👤 @{update.effective_user.username}\n📌 {subject}\nMasala: {text or 'Matn mavjud emas'}")
        elif document:
            storage_msg = await bot.send_document(CHANNEL_ID, document.file_id,
                                                  caption=f"👤 @{update.effective_user.username}\n📌 {subject}\nMasala: {text or 'Matn mavjud emas'}")
        else:
            storage_msg = await bot.send_message(CHANNEL_ID,
                                                 f"👤 @{update.effective_user.username}\n📌 {subject}\nMasala: {text or 'Matn mavjud emas'}")

        # Save to JSON
        user_data = json_data["users"].setdefault(str(user_id), {
            "username": update.effective_user.username or "NoUsername",
            "masala_count": 0,
            "join_date": str(datetime.datetime.now()),
            "problems": {}
        })
        user_data["masala_count"] += 1
        user_data["problems"][str(update.message.message_id)] = {
            "subject": subject,
            "channel_msg_id": storage_msg.message_id,
            "status": "pending"
        }
        save_data(json_data)
        pending_users.pop(user_id)

        # Notify admin
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("❌ Masalada kamchilik", callback_data=f"masala_error_{update.message.message_id}_{user_id}"),
                InlineKeyboardButton("📤 Yechim yuborish", callback_data=f"send_solution_{update.message.message_id}_{user_id}")
            ]
        ])
        # Forward the stored message from the channel to the admin
        await bot.forward_message(
    chat_id=ADMIN_ID,
    from_chat_id=CHANNEL_ID,
    message_id=storage_msg.message_id
)
        await bot.send_message(ADMIN_ID, "..............................", reply_markup=kb)
        await bot.send_message(user_id, f"📤 Masalangiz qabul qilindi va adminga yuborildi.✅\n⏳Admin yechim yuborishini kuting yoki boshqa masala yuboring")
        return

    # --- ADMIN sends solution ---
    if user_id == ADMIN_ID and admin_pending_solution.get(ADMIN_ID):
        target_user_id, target_msg_id = admin_pending_solution[ADMIN_ID]
        problem = json_data["users"][str(target_user_id)]["problems"][str(target_msg_id)]
        # Send to user
        await bot.send_message(
            chat_id=target_user_id,
            text=text or "Yechim matni mavjud emas",
            reply_to_message_id=int(target_msg_id)
        )
        # Rating buttons
        kb = InlineKeyboardMarkup([
            [InlineKeyboardButton(str(i), callback_data=f"rate_{i}_{target_user_id}_{target_msg_id}") for i in range(1, 6)],
            [InlineKeyboardButton(str(i), callback_data=f"rate_{i}_{target_user_id}_{target_msg_id}") for i in range(6, 11)]
        ])
        await bot.send_message(target_user_id, "📊 Yechimni baholang (1–juda yomon, 10–juda zo'r):", reply_markup=kb)

        # Also post solution to storage channel
        await bot.send_message(CHANNEL_ID, text or "Yechim matni mavjud emas",
                               reply_to_message_id=int(problem["channel_msg_id"]))

        problem["status"] = "solved"
        save_data(json_data)
        admin_pending_solution.pop(ADMIN_ID)
        return

# --- APP SETUP ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("masala", masala))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.ALL, message_handler))

print("Bot ishga tushdi ✅")
app.run_polling()
