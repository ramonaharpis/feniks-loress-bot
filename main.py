import discord
from discord.ext import commands
import random
import asyncio
import os

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

karty = [
    "Karta 01 Harry Potter", "Karta 02 Hermiona Granger",
    "Karta 03 Ron Weasley", "Karta 04 Albus Dumbledore",
    "Karta 05 Minerwa McGonagall", "Karta 06 Severus Snape",
    "Karta 07 Rubeus Hagrid", "Karta 08 Kieł", "Karta 09 Draco Malfoy",
    "Karta 10 Luna Lovegood", "Karta 11 Neville Longbottom",
    "Karta 12 Cho Chang", "Karta 13 Voldemort", "Karta 14 Hedwiga",
    "Karta 15 Hogwart"
]

OWNER_ID = 1052041798048026664
DOZWOLONY_KANAL_KART = 1391801753082531981

karta_aktywowana = False

@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")

@bot.command()
async def kartastart(ctx):
    global karta_aktywowana
    if ctx.author.id != OWNER_ID:
        return
    karta_aktywowana = True
    await ctx.send("🔓 Niech wszyscy losują swoją kartę!")

@bot.command()
async def karta(ctx):
    global karta_aktywowana
    if not karta_aktywowana:
        await ctx.send("❌ Karty są obecnie zablokowane.")
        return
    wylosowana = random.choice(karty)
    await ctx.send(f"**{ctx.author.display_name}**, Twoja karta to: **{wylosowana}** ✨")

@bot.command()
async def kartastop(ctx):
    global karta_aktywowana
    if ctx.author.id != OWNER_ID:
        return
    karta_aktywowana = False
    await ctx.send("🔒 Losowanie kart zakończone!")

import os
bot.run(os.getenv("DISCORD_TOKEN"))
