# 📝 EduHelper Bot

**EduHelper Bot** is a Telegram bot designed for students to submit subject-specific problems and receive solutions from an admin. It supports multiple subjects, image/file uploads, and a user feedback/rating system. All submissions and solutions are stored in a private Telegram channel for easy tracking.

---

## 🚀 Features

* **Multi-subject support**: Mathematics, Physics, Chemistry, Biology, Computer Science, Geography, History, Literature, and more.
* **Submit problems via text, image, or file**.
* **Admin management**: Admin can mark problems as solved, request corrections, and send solutions.
* **Inline buttons**: User-friendly buttons for submitting, canceling, changing subjects, and rating solutions.
* **Solution rating system**: Users can rate solutions from 1–10 stars and optionally leave a comment.
* **Storage channel integration**: All problems and solutions are forwarded to a private Telegram channel.
* **JSON-based persistent storage**: Keeps track of users, problems, and solution statuses.

---

## 🛠 Installation

1. **Clone the repository**:

```bash
git clone https://github.com/yourusername/eduhelper-bot.git
cd eduhelper-bot
```

2. **Set up a virtual environment** (recommended):

```bash
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate     # Windows
```

3. **Install dependencies**:

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file** or set your tokens inside the bot file:

```env
BOT_TOKEN=your_telegram_bot_token
ADMIN_ID=your_telegram_user_id
CHANNEL_ID=your_private_storage_channel_id
```

---

## ⚡ Usage

* Start the bot:

```bash
python bot.py
```

* **User commands**:

  * `/start` – Show welcome message and instructions
  * `/masala` – Start submitting a new problem

* **Admin workflow**:

  * Receives problem submissions with inline buttons:

    * ❌ Masalada kamchilik → mark as error
    * 📤 Yechim yuborish → send solution
  * Solutions are forwarded to storage channel and sent to user.
  * User ratings are received and linked to the storage channel post.

---

## 📂 Data Storage

* `bot_data.json` is used to persist user data:

```json
{
  "users": {
    "123456789": {
      "username": "student1",
      "masala_count": 3,
      "join_date": "2025-12-16T12:34:56",
      "problems": {
        "56789": {
          "subject": "Matematika",
          "channel_msg_id": 101112,
          "status": "solved"
        }
      }
    }
  }
}
```

* Each problem includes:

  * Subject
  * Storage channel message ID
  * Status: `pending`, `solved`, `error`

---

## 💡 Notes

* Private storage channel must allow the bot to **post and read messages**.
* Admin must be aware of the channel ID and bot token configuration.
* Ensure bot has permission to **send messages and media** to users and the channel.

---

## 🔗 Useful Links

* [Telegram Bot API Documentation](https://core.telegram.org/bots/api)
* [Python Telegram Bot Library](https://python-telegram-bot.readthedocs.io/)

---

## 📌 Contributing

Contributions are welcome! You can:

* Add new subjects
* Improve UI text and feedback messages
* Add analytics for problems submitted per subject

---

## 📝 License

MIT License © 2025 — Open for educational and personal use
