import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Replace with your Telegram bot token
TELEGRAM_BOT_TOKEN = "6126511065:AAHLPF8CuwowgQm9NaYK_vR_caAD_c0tCxg"

# Replace with your Judge0 API endpoint
JUDGE0_API_URL = "https://ce.judge0.com/submissions"

# Language ID mapping for Judge0 API
LANGUAGES = {
    "python": 71,
    "java": 62,
    "c": 50,
    "cpp": 54,
    "html": 68,
    "ruby": 72,
    "go": 20,
    # Add more languages as needed
}

def start(update, context):
    update.message.reply_text("Hello! I am an online compiler bot. Send me your code!")

def compile_code(update, context):
    user_code = update.message.text.strip()

    # Extract language tag from the user's message (e.g., "#python")
    if user_code.startswith("#"):
        lang_tag, user_code = user_code.split(maxsplit=1)
        language = lang_tag[1:].lower()  # Remove '#' and convert to lowercase
    else:
        # If no language tag is provided, default to Python
        language = "python"

    # Check if the language is supported
    if language not in LANGUAGES:
        update.message.reply_text(f"Sorry, the '{language}' language is not supported.")
        return

    language_id = LANGUAGES[language]

    # Compile code using Judge0 API
    response = requests.post(f"{JUDGE0_API_URL}/submissions/?wait=true", json={
        "source_code": user_code,
        "language_id": language_id,
    })

    if response.status_code == 201:
        output = response.json()["stdout"]
        update.message.reply_text(f"Output:\n{output}")
    else:
        update.message.reply_text("Sorry, an error occurred while compiling your code.")

def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, compile_code))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

