import discord
from discord.ext import commands
import random
import asyncio
import os  # jeśli używasz zmiennych środowiskowych (sekretów na Replit)

# ----------------------
# Ustawienia bota
# ----------------------
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ----------------------
# ID kanałów
# ----------------------
DOZWOLONY_KANAL_KART = 1391801753082531981
DOZWOLONY_KANAL_LOSOWANIE = 1391802487434121295
DOZWOLONY_KANAL_POJEDYNKÓW = 1415643645717250142

# ----------------------
# Lista kart
# ----------------------
karty = [
    "Karta 01 Harry Potter", "Karta 02 Hermiona Granger",
    "Karta 03 Ron Weasley", "Karta 04 Albus Dumbledore",
    "Karta 05 Minerwa McGonagall", "Karta 06 Severus Snape",
    "Karta 07 Rubeus Hagrid", "Karta 08 Kieł", "Karta 09 Draco Malfoy",
    "Karta 10 Luna Lovegood", "Karta 11 Neville Longbottom",
    "Karta 12 Cho Chang", "Karta 13 Voldemort", "Karta 14 Hedwiga",
    "Karta 15 Hogwart"
]

# ----------------------
# Karty zmienne
# ----------------------
karta_aktywowana = False
OWNER_ID = 1052041798048026664  # Twój ID

# ----------------------
# Pojedynki zmienne
# ----------------------
pojedynek_aktywny = False
gracz1_obj = None
gracz2_obj = None
hp = {}
czekamy_na_obrone = False
ostatnie_zaklecia = {}  # do limitu użycia zaklęć pod rząd

# ----------------------
# Dodatkowe zmienne (festyn)
# ----------------------
rzuty_graczy = {}  # licznik rzutów kasztanem

# ----------------------
# Zaklęcia
# ----------------------
SPELLS = {
    "flipendo": {
        "kat": 1,
        "cast_chance": 80,
        "damage": 10
    },
    "expelliarmus": {
        "kat": 2,
        "cast_chance": 75,
        "damage": 15
    },
    "drętwota": {
        "kat": 3,
        "cast_chance": 65,
        "damage": 25
    },
}

DEFENSES = {
    "unik": {
        "cast_chance": 90,
        "vs": {
            1: 75,
            2: 50,
            3: 25
        }
    },
    "protego": {
        "cast_chance": 80,
        "vs": {
            1: 40,
            2: 70,
            3: 30
        }
    },
    "protegomaxima": {
        "cast_chance": 70,
        "vs": {
            1: 40,
            2: 50,
            3: 75
        }
    },
}


# ----------------------
# Funkcje pomocnicze
# ----------------------
def check_channel(ctx, kanal):
    return ctx.channel.id == kanal


def get_ofiara(atakujacy):
    return gracz1_obj if atakujacy == gracz2_obj else gracz2_obj


def pasek_hp(gracz):
    total = 100
    current = hp[gracz]
    fill = int((current / total) * 10)
    empty = 10 - fill
    return f"[{'█'*fill}{'░'*empty}] {current}/100 HP"


async def reset_pojedynek():
    global pojedynek_aktywny, gracz1_obj, gracz2_obj, hp, czekamy_na_obrone, ostatnie_zaklecia
    pojedynek_aktywny = False
    gracz1_obj = None
    gracz2_obj = None
    hp = {}
    czekamy_na_obrone = False
    ostatnie_zaklecia = {}


def sprawdz_powtorzenia(gracz, spell_name):
    if gracz.id not in ostatnie_zaklecia:
        ostatnie_zaklecia[gracz.id] = []
    if ostatnie_zaklecia[gracz.id].count(spell_name) >= 2:
        return False
    ostatnie_zaklecia[gracz.id].append(spell_name)
    # utrzymuj tylko 3 ostatnie zaklęcia
    if len(ostatnie_zaklecia[gracz.id]) > 3:
        ostatnie_zaklecia[gracz.id].pop(0)
    return True


# ----------------------
# Event logowania
# ----------------------
@bot.event
async def on_ready():
    print(f"✅ Zalogowano jako {bot.user}")


# ----------------------
# Komendy Kart
# ----------------------
@bot.command()
async def kartastart(ctx):
    global karta_aktywowana
    if ctx.author.id != OWNER_ID:
        return
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    karta_aktywowana = True
    await ctx.send("🔓 Niech wszyscy losują swoją kartę!")


@bot.command()
async def karta(ctx):
    global karta_aktywowana
    autor = ctx.author.display_name
    if not check_channel(ctx, DOZWOLONY_KANAL_KART):
        await ctx.send("❌ Ta komenda działa tylko na kanale - MagiKarty.")
        return
    if not karta_aktywowana:
        await ctx.send(f"**{autor}** Nie oszukuj z kartami!")
        return
    wylosowana = random.choice(karty)
    await ctx.send(f"**{autor}**, Twoja wylosowana karta to **{wylosowana}**!")


@bot.command()
async def kartastop(ctx):
    global karta_aktywowana
    if ctx.author.id != OWNER_ID:
        return
    try:
        await ctx.message.delete()
    except discord.Forbidden:
        pass
    karta_aktywowana = False
    await ctx.send("🔒 Koniec losowania kart!")


@bot.command()
async def losowanie(ctx):
    if not check_channel(ctx, DOZWOLONY_KANAL_LOSOWANIE):
        await ctx.send("❌ Ta komenda działa tylko na kanale loresslos.")
        return
    wyniki = random.sample(range(1, 9), 3)
    await ctx.send(
        f"🎲 Dzisiejsze wylosowane cyfry to: {wyniki[0]}, {wyniki[1]}, {wyniki[2]} 💰"
    )


@bot.command()
async def kanal_id(ctx):
    await ctx.send(f"📌 ID tego kanału to: `{ctx.channel.id}`")


# ----------------------
# Komendy pojedynków
# ----------------------
@bot.command()
async def pojedynki(ctx):
    global pojedynek_aktywny
    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW):
        return
    if pojedynek_aktywny:
        await ctx.send("Pojedynek już trwa!")
        return
    pojedynek_aktywny = True
    await ctx.send(
        "Rozpoczynamy nowy pojedynek! Gracze zgłaszają się komendami `!gracz1` i `!gracz2`."
    )


@bot.command()
async def gracz1(ctx):
    global gracz1_obj, hp
    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW):
        return
    if gracz1_obj is None:
        gracz1_obj = ctx.author
        hp[gracz1_obj] = 100
        await ctx.send(
            f"Gracz1 to **{ctx.author.display_name}** (HP: {pasek_hp(ctx.author)})"
        )
    else:
        await ctx.send("Gracz1 został wybrany.")


@bot.command()
async def gracz2(ctx):
    global gracz2_obj, hp
    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW):
        return
    if gracz2_obj is None:
        gracz2_obj = ctx.author
        hp[gracz2_obj] = 100
        await ctx.send(
            f"Gracz2 to **{ctx.author.display_name}** (HP: {pasek_hp(ctx.author)})"
        )
    else:
        await ctx.send("Gracz2 został wybrany.")


@bot.command()
async def start(ctx):
    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW):
        return
    if not gracz1_obj or not gracz2_obj:
        await ctx.send("Najpierw muszą zgłosić się obaj gracze!")
        return
    await ctx.send(
        f"Pojedynek pomiędzy **{gracz1_obj.display_name}** a **{gracz2_obj.display_name}**! "
        f"Rzucajcie zaklęcia: `!flipendo`, `!expelliarmus`, `!drętwota`."
    )


@bot.command()
async def koniec(ctx):
    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW):
        return
    if not pojedynek_aktywny:
        await ctx.send("Nie ma aktywnego pojedynku.")
        return
    await ctx.send("Pojedynek zakończony.")
    await reset_pojedynek()


# ----------------------
# Obsługa ataku i obrony
# ----------------------
async def atak(ctx, spell_name):
    global czekamy_na_obrone
    atakujacy = ctx.author

    if not check_channel(ctx, DOZWOLONY_KANAL_POJEDYNKÓW) or not pojedynek_aktywny:
        return
    if atakujacy not in [gracz1_obj, gracz2_obj]:
        return
    if czekamy_na_obrone:
        await ctx.send("Czekamy na rozstrzygnięcie poprzedniego zaklęcia!")
        return
    if not sprawdz_powtorzenia(atakujacy, spell_name):
        await ctx.send(
            f"❌ Nie możesz użyć **{spell_name}** więcej niż 2 razy pod rząd!"
        )
        return

    spell = SPELLS[spell_name]
    ofiara = get_ofiara(atakujacy)

    if random.randint(1, 100) > spell["cast_chance"]:
        await ctx.send(
            f"**{atakujacy.display_name}** próbował rzucić **{spell_name.capitalize()}**, ale zaklęcie się nie powiodło!"
        )
        return

    await ctx.send(
        f"**{atakujacy.display_name}** rzucił **{spell_name.capitalize()}**! "
        f"**{ofiara.display_name}** ma 5 sekund na obronę: `!unik`, `!protego`, `!protegomaxima`!"
    )
    czekamy_na_obrone = True

    try:
        await asyncio.wait_for(obrona(ctx, ofiara, atakujacy, spell), timeout=5)
    except asyncio.TimeoutError:
        hp[ofiara] -= spell["damage"]
        await ctx.send(
            f"**{ofiara.display_name}** nie zdążył się obronić! Traci {spell['damage']} HP. {pasek_hp(ofiara)}"
        )
        if hp[ofiara] <= 0:
            await ctx.send(
                f"**{ofiara.display_name}** został pokonany! Zwycięzcą jest **{atakujacy.display_name}** 🎉"
            )
            await reset_pojedynek()
    czekamy_na_obrone = False


async def obrona(ctx, ofiara, atakujacy, spell):
    global czekamy_na_obrone

    def check(m):
        return (
            m.author == ofiara
            and m.channel.id == ctx.channel.id
            and m.content.lower().strip()
            in ["!unik", "!protego", "!protegomaxima"]
        )

    try:
        msg = await bot.wait_for("message", check=check, timeout=5)
    except asyncio.TimeoutError:
        hp[ofiara] -= spell["damage"]
        await ctx.send(
            f"**{ofiara.display_name}** nie zdążył się obronić! Traci {spell['damage']} HP. {pasek_hp(ofiara)}"
        )
        return

    defense_name = msg.content.lower().strip().replace("!", "")
    defense = DEFENSES[defense_name]

    if not sprawdz_powtorzenia(ofiara, defense_name):
        await ctx.send(
            f"❌ Nie możesz użyć **{defense_name}** więcej niż 2 razy pod rząd!"
        )
        hp[ofiara] -= spell["damage"]
        await ctx.send(
            f"**{ofiara.display_name}** traci {spell['damage']} HP. {pasek_hp(ofiara)}"
        )
        return

    if random.randint(1, 100) > defense["cast_chance"]:
        hp[ofiara] -= spell["damage"]
        await ctx.send(
            f"**{ofiara.display_name}** rzucił **{defense_name.capitalize()}**, ale zaklęcie się nie powiodło! "
            f"Traci {spell['damage']} HP. {pasek_hp(ofiara)}"
        )
    else:
        skutecznosc = defense["vs"][spell["kat"]]
        if random.randint(1, 100) <= skutecznosc:
            await ctx.send(
                f"**{ofiara.display_name}** skutecznie obronił się zaklęciem **{defense_name.capitalize()}**!"
            )
        else:
            hp[ofiara] -= spell["damage"]
            await ctx.send(
                f"**{ofiara.display_name}** próbował obrony **{defense_name.capitalize()}**, ale zaklęcie przebiło obronę. "
                f"Traci {spell['damage']} HP. {pasek_hp(ofiara)}"
            )

    if hp[ofiara] <= 0:
        await ctx.send(
            f"**{ofiara.display_name}** został pokonany! Zwycięzcą jest **{atakujacy.display_name}** 🎉"
        )
        await reset_pojedynek()


# ----------------------
# Komendy zaklęć atakujących
# ----------------------
@bot.command()
async def flipendo(ctx):
    await atak(ctx, "flipendo")


@bot.command()
async def expelliarmus(ctx):
    await atak(ctx, "expelliarmus")


@bot.command()
async def drętwota(ctx):
    await atak(ctx, "drętwota")


# ----------------------
# Komendy obronne
# ----------------------
@bot.command()
async def unik(ctx):
    pass


@bot.command()
async def protego(ctx):
    pass


@bot.command()
async def protegomaxima(ctx):
    pass


# ----------------------
# Uruchomienie bota
# ----------------------
bot.run(os.getenv("MTM2MjQ0OTk2MDAwMzY5ODczOA.GTzVW4.9YV86ygFvVXsxlgHysGZr4KyJ9q7sM_iDeJUpE"))
