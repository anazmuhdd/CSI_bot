# discord_bot.py
import discord
import requests
import asyncio

TOKEN = ""  # Replace with your actual bot token
FLASK_BACKEND_URL = "http://127.0.0.1:5001/process" 

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # Respond only to direct messages (DMs)
    if isinstance(message.channel, discord.DMChannel):
        user_input = message.content
        user_id = str(message.author.id)
        print(f"Received message from user {user_id}: {user_input}")
        try:
            # Send user message to your Flask backend
            response = requests.post(FLASK_BACKEND_URL, json={
                "message": user_input,
                "user_id": user_id
            })

            reply = response.json().get("reply", "Sorry, something went wrong.")
            await message.channel.send(reply)
            print(f"Reply sent to user {user_id}: {reply}")
        except Exception as e:
            print(f"Error: {e}")
            await message.channel.send("Sorry, I couldn't process your request.")

client.run(TOKEN)
