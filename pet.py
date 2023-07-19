import os
import sqlite3
from pyrogram import Client, filters, idle
from pyrogram.types import Message

# Initialize the Pyrogram client and connect to the Telegram Bot API
api_id =  16743442
api_hash = '12bbd720f4097ba7713c5e40a11dfd2a'
bot_token = '6377102011:AAHJJ7AUKZhQKcAnHPQtjg9put5mG8vSjEc'

app = Client("my_bot", api_id=api_id, api_hash=api_hash, bot_token=bot_token)

# Initialize the SQLite database
db_file = "pet_bot.db"
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Create a table to store pet data
cursor.execute("""
CREATE TABLE IF NOT EXISTS pets (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    health INTEGER,
    hunger INTEGER,
    happiness INTEGER
)
""")
conn.commit()

# Define the virtual pet class
class Pet:
    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.health = 100
        self.hunger = 0
        self.happiness = 100

    def feed(self):
        self.hunger -= 10
        if self.hunger < 0:
            self.hunger = 0
        self.happiness += 5
        if self.happiness > 100:
            self.happiness = 100

    def play(self):
        self.hunger += 5
        if self.hunger > 100:
            self.hunger = 100
        self.happiness += 10
        if self.happiness > 100:
            self.happiness = 100

# Define command handlers
@app.on_message(filters.command("start"))
def start(bot, message):
    bot.send_message(
        message.chat.id,
        "Hello! I am your virtual pet bot. Use /adopt <pet_name> to adopt a pet."
    )


# Define a list of suggested pet names
suggested_names = ["Buddy", "Fluffy", "Charlie", "Luna", "Max", "Coco", "Oliver", "Daisy", "Tom"]

# Help command
@app.on_message(filters.command("help"))
def show_help(bot, message):
    help_text = """Available commands:
/adopt <pet_name> - Adopt a virtual pet.
/feed - Feed your pet.
/play - Play with your pet.
/status - Check your pet's status.
/help - Show this help message."""
    bot.send_message(message.chat.id, help_text)

# Adopt a pet with a suggested name
@app.on_message(filters.command("adopt"))
def adopt_pet(bot, message):
    if len(message.command) < 2:
        bot.send_message(message.chat.id, "Please provide a name for your pet. Use /adopt <pet_name>.")
        return

    pet_name = message.command[1]
    user_id = message.from_user.id

    # Check if the user already has a pet
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    existing_pet = cursor.fetchone()

    if existing_pet:
        bot.send_message(message.chat.id, "You already have a pet.")
    else:
        if pet_name.lower() in [name.lower() for name in suggested_names]:
            new_pet = Pet(user_id, pet_name)
        else:
            bot.send_message(
                message.chat.id,
                f"The name '{pet_name}' is not in the list of suggested names. Choose from: {', '.join(suggested_names)}"
            )
            return

        cursor.execute("INSERT INTO pets VALUES (?, ?, ?, ?, ?)", (user_id, pet_name, new_pet.health, new_pet.hunger, new_pet.happiness))
        conn.commit()
        bot.send_message(message.chat.id, f"Congratulations! You adopted a pet named {pet_name}.")

# Feed the pet
@app.on_message(filters.command("feed"))
def feed_pet(bot, message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    pet_data = cursor.fetchone()

    if not pet_data:
        bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> to adopt one.")
        return

    pet = Pet(pet_data[0], pet_data[1])
    pet.feed()

    cursor.execute("UPDATE pets SET hunger=?, happiness=? WHERE user_id=?", (pet.hunger, pet.happiness, user_id))
    conn.commit()

    bot.send_message(message.chat.id, f"{pet.name} has been fed. Hunger: {pet.hunger}, Happiness: {pet.happiness}")

# Play with the pet
@app.on_message(filters.command("play"))
def play_with_pet(bot, message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    pet_data = cursor.fetchone()

    if not pet_data:
        bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> to adopt one.")
        return

    pet = Pet(pet_data[0], pet_data[1])
    pet.play()

    cursor.execute("UPDATE pets SET hunger=?, happiness=? WHERE user_id=?", (pet.hunger, pet.happiness, user_id))
    conn.commit()

    bot.send_message(message.chat.id, f"{pet.name} is happy! Hunger: {pet.hunger}, Happiness: {pet.happiness}")

# Check the pet's status
@app.on_message(filters.command("status"))
def check_pet_status(bot, message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
    pet_data = cursor.fetchone()

    if not pet_data:
        bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> to adopt one.")
        return

    pet = Pet(pet_data[0], pet_data[1])

    bot.send_message(
        message.chat.id,
        f"Pet Name: {pet.name}\nHealth: {pet.health}\nHunger: {pet.hunger}\nHappiness: {pet.happiness}"
    )

# ... Add other commands and features as needed ...

# Run the bot
app.run()
print('bot started')
idle()
