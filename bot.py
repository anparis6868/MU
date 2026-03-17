import os
import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 123456789  # 👉 thay bằng ID kênh Discord của bạn

client = discord.Client(intents=discord.Intents.default())

characters = {
    "HARD": {
        "url": "https://elitemu.net/character/4368616e/HARD",
        "last_level": 0,
        "last_death": ""
    }
}

def get_data(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    text = soup.get_text()

    level = None
    for line in text.split("\n"):
        if "Level" in line:
            try:
                level = int(''.join(filter(str.isdigit, line)))
                break
            except:
                pass

    death = None
    if "Kill Time" in text:
        lines = text.split("\n")
        for i, line in enumerate(lines):
            if "Kill Time" in line:
                death = lines[i+1].strip()
                break

    return level, death


@tasks.loop(seconds=20)
async def tracker():
    channel = client.get_channel(CHANNEL_ID)

    for name, data in characters.items():
        level, death = get_data(data["url"])

        if level is None:
            continue

        if level >= 400 and data["last_level"] < 400:
            await channel.send(f"🔥 {name} đủ 400 → RESET!")

        if death and death != data["last_death"]:
            await channel.send(f"💀 {name} vừa bị giết!\n{death}")

        data["last_level"] = level
        data["last_death"] = death


@client.event
async def on_ready():
    print("Bot đang chạy...")
    tracker.start()

client.run(TOKEN)
