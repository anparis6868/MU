import os
import discord
from discord.ext import tasks
import requests
from bs4 import BeautifulSoup

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = 1483361517066915842  # ID kênh của bạn

client = discord.Client(intents=discord.Intents.default())

# 🔥 DANH SÁCH NHÂN VẬT
characters = {
    "SM": {
        "url": "https://elitemu.net/character/4368616e/HARD",
        "last_level": 0,
        "last_death": ""
    },

    "MG": {
        "url": "https://elitemu.net/character/5472616e48616f4e616d/HARD",
        "last_level": 0,
        "last_death": ""
    },

    "DL": {
        "url": "https://elitemu.net/character/4e6f54776f/HARD",
        "last_level": 0,
        "last_death": ""
    },

    "RF": {
        "url": "https://elitemu.net/character/4f69536869/HARD",
        "last_level": 0,
        "last_death": ""
    }
}

# 🔍 LẤY DỮ LIỆU TỪ WEB
def get_data(url):
    try:
        r = requests.get(url, timeout=10)
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
                if "Kill Time" in line and i + 1 < len(lines):
                    death = lines[i+1].strip()
                    break

        return level, death
    except:
        return None, None


# 🔄 LOOP THEO DÕI
@tasks.loop(seconds=30)
async def tracker():
    channel = client.get_channel(CHANNEL_ID)

    for name, data in characters.items():
        level, death = get_data(data["url"])

        if level is None:
            continue

        # 📈 LÊN LEVEL
        if level != data["last_level"]:
            await channel.send(f"📈 {name} lên level {level}")
            data["last_level"] = level

        # 🔥 ĐỦ 400
        if level >= 400 and data["last_level"] < 400:
            await channel.send(f"🔥 {name} đủ 400 → RESET NGAY!")

        # 💀 BỊ GIẾT
        if death and death != data["last_death"]:
            await channel.send(f"💀 {name} vừa bị giết!\n{death}")
            data["last_death"] = death


# ✅ BOT READY
@client.event
async def on_ready():
    print("Bot đang chạy...")
    channel = client.get_channel(CHANNEL_ID)
    if channel:
        await channel.send("🤖 Bot MU đã online!")
    tracker.start()


client.run(TOKEN)
