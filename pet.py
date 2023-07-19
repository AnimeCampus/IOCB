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

# Define the virtual pet class
class Pet:
    def __init__(self, user_id, name, pet_type):
        self.user_id = user_id
        self.name = name
        self.pet_type = pet_type
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

# Helper function to create the pets table if it doesn't exist
def create_pets_table():
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS pets (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            pet_type TEXT,
            health INTEGER,
            hunger INTEGER,
            happiness INTEGER
        )
        """)
        conn.commit()

# Command to show the user's current pet's name and type
@app.on_message(filters.command("store"))
def show_pet_store(bot, message):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        user_id = message.from_user.id
        cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
        pet_data = cursor.fetchone()

        if not pet_data:
            bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> <dog|cat|other> to adopt one.")
            return

        pet_name, pet_type = pet_data[1], pet_data[2]
        bot.send_message(message.chat.id, f"Your current pet: {pet_name} ({pet_type.capitalize()})")

# Command to adopt a pet with a suggested name and type
@app.on_message(filters.command("adopt"))
def adopt_pet(bot, message):
    if len(message.command) < 3:
        bot.send_message(message.chat.id, "Please provide both a name and a type for your pet. Use /adopt <pet_name> <dog|cat|other>.")
        return

    pet_name = message.command[1]
    pet_type = message.command[2].lower()
    user_id = message.from_user.id

    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        # Check if the user already has a pet
        cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
        existing_pet = cursor.fetchone()

        if existing_pet:
            bot.send_message(message.chat.id, "You already have a pet.")
        else:
            new_pet = Pet(user_id, pet_name, pet_type)
            cursor.execute("INSERT INTO pets VALUES (?, ?, ?, ?, ?, ?)", (user_id, pet_name, pet_type, new_pet.health, new_pet.hunger, new_pet.happiness))
            conn.commit()
            bot.send_message(message.chat.id, f"Congratulations! You adopted a {pet_type} named {pet_name}.")

# Command to feed the pet
@app.on_message(filters.command("feed"))
def feed_pet(bot, message):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        user_id = message.from_user.id
        cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
        pet_data = cursor.fetchone()

        if not pet_data:
            bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> <dog|cat|other> to adopt one.")
            return

        pet = Pet(pet_data[0], pet_data[1], pet_data[2])
        pet.feed()

        cursor.execute("UPDATE pets SET hunger=?, happiness=? WHERE user_id=?", (pet.hunger, pet.happiness, user_id))
        conn.commit()

        bot.send_message(message.chat.id, f"{pet.name} has been fed. Hunger: {pet.hunger}, Happiness: {pet.happiness}")

# Command to show the available commands and their usage
@app.on_message(filters.command("help"))
def show_help(bot, message):
    help_text = """Available commands:
/adopt <pet_name> <dog|cat|other> - Adopt a virtual pet.
/feed - Feed your pet.
/play - Play with your pet.
/status - Check your pet's status.
/store - Show your current pet's name and type.
/help - Show this help message."""
    bot.send_message(message.chat.id, help_text)

# Command to play with the pet
@app.on_message(filters.command("play"))
def play_with_pet(bot, message):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        user_id = message.from_user.id
        cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
        pet_data = cursor.fetchone()

        if not pet_data:
            bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> <dog|cat|other> to adopt one.")
            return

        pet = Pet(pet_data[0], pet_data[1], pet_data[2])
        pet.play()

        cursor.execute("UPDATE pets SET hunger=?, happiness=? WHERE user_id=?", (pet.hunger, pet.happiness, user_id))
        conn.commit()

        bot.send_message(message.chat.id, f"{pet.name} is happy! Hunger: {pet.hunger}, Happiness: {pet.happiness}")

# Command to check the pet's status
@app.on_message(filters.command("status"))
def check_pet_status(bot, message):
    with sqlite3.connect(db_file) as conn:
        cursor = conn.cursor()

        user_id = message.from_user.id
        cursor.execute("SELECT * FROM pets WHERE user_id=?", (user_id,))
        pet_data = cursor.fetchone()

        if not pet_data:
            bot.send_message(message.chat.id, "You don't have a pet yet. Use /adopt <pet_name> <dog|cat|other> to adopt one.")
            return

        pet = Pet(pet_data[0], pet_data[1], pet_data[2])

        bot.send_message(
            message.chat.id,
            f"Pet Name: {pet.name}\nType: {pet.pet_type.capitalize()}\nHealth: {pet.health}\nHunger: {pet.hunger}\nHappiness: {pet.happiness}"
        )

# ... Add other commands and features as needed ...

# Create the pets table if it doesn't exist
create_pets_table()

# Run the bot
app.run()
print('bot started')
idle()
