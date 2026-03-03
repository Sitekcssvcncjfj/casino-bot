import random
import sqlite3
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = "8775727673:AAEbdY7ILordYEPHpk5yxkzy6wVL-2uKnhY"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

ADMINS = [6101127840, 8189353497]

# DATABASE
conn = sqlite3.connect("casino.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    sikke INTEGER,
    bank INTEGER DEFAULT 0
)
""")
conn.commit()


# USER GET
def get_user(user_id, username):

    cursor.execute("SELECT sikke FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    if data is None:
        cursor.execute(
            "INSERT INTO users (user_id, username, sikke, bank) VALUES (?, ?, ?, ?)",
            (user_id, username, 1000, 0)
        )
        conn.commit()
        return 1000

    else:
        cursor.execute(
            "UPDATE users SET username=? WHERE user_id=?",
            (username, user_id)
        )
        conn.commit()

        return data[0]


# UPDATE COIN
def update_sikke(user_id, amount):

    cursor.execute("SELECT sikke FROM users WHERE user_id=?", (user_id,))
    data = cursor.fetchone()

    if data is None:
        return

    sikke = data[0]

    sikke += amount

    if sikke < 0:
        sikke = 0

    cursor.execute(
        "UPDATE users SET sikke=? WHERE user_id=?",
        (sikke, user_id)
    )
    conn.commit()


# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    get_user(user, name)

    await update.message.reply_text(
        "🎰 Amınoğlu Casino'ya hoşgeldin!\n"
        "Başlangıç bakiyesi: 1000 🪙"
    )


# BALANCE
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    sikke = get_user(user, name)

    vip = ""
    if sikke >= 50000:
        vip = "💎 VIP Oyuncu\n"

    await update.message.reply_text(
        f"{vip}💰 Bakiyen: {sikke} 🪙"
    )


# RULET
async def rulet(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
        renk = context.args[1]
    except:
        await update.message.reply_text("/rulet miktar kırmızı/siyah")
        return

    if sikke < bet:
        await update.message.reply_text("❌ Yetersiz bakiye")
        return

    sonuc = random.choice(["kırmızı", "siyah"])

    if renk == sonuc:

        win = bet * 2
        update_sikke(user, win)

        text = f"🎡 Rulet: {sonuc}\n🎉 Kazandın +{win}"

    else:

        update_sikke(user, -bet)

        text = f"🎡 Rulet: {sonuc}\n😢 Kaybettin -{bet}"

    await update.message.reply_text(text)


# BLACKJACK
async def blackjack(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
    except:
        await update.message.reply_text("/blackjack miktar")
        return

    if sikke < bet:
        await update.message.reply_text("❌ Bakiye yok")
        return

    player = random.randint(15, 21)
    bot = random.randint(15, 21)

    if player > bot:
        update_sikke(user, bet)
        text = f"🃏 Sen:{player}\n🤖 Bot:{bot}\n🎉 Kazandın +{bet}"

    elif player < bot:
        update_sikke(user, -bet)
        text = f"🃏 Sen:{player}\n🤖 Bot:{bot}\n😢 Kaybettin -{bet}"

    else:
        text = "🤝 Berabere"

    await update.message.reply_text(text)


# POKER
async def poker(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
    except:
        await update.message.reply_text("/poker miktar")
        return

    if sikke < bet:
        await update.message.reply_text("❌ Bakiye yok")
        return

    player = random.randint(1, 100)
    bot = random.randint(1, 100)

    if player > bot:
        update_sikke(user, bet * 2)
        text = f"♠️ Poker kazandın +{bet*2}"

    else:
        update_sikke(user, -bet)
        text = f"♠️ Kaybettin -{bet}"

    await update.message.reply_text(text)


# SLOT
async def slot(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
    except:
        bet = 50

    if sikke < bet:
        await update.message.reply_text("❌ Yetersiz bakiye")
        return

    msg = await update.message.reply_dice(emoji="🎰")
    value = msg.dice.value

    if value > 50:
        win = bet * 5
        update_sikke(user, win)
        text = f"🎉 JACKPOT +{win} 🪙"

    elif value > 25:
        win = bet * 2
        update_sikke(user, win)
        text = f"🙂 Kazandın +{win} 🪙"

    else:
        update_sikke(user, -bet)
        text = f"😢 Kaybettin -{bet} 🪙"

    await update.message.reply_text(text)


# ZAR
async def zar(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
    except:
        bet = 50

    if sikke < bet:
        await update.message.reply_text("❌ Yetersiz bakiye")
        return

    msg = await update.message.reply_dice(emoji="🎲")
    player = msg.dice.value
    bot = random.randint(1,6)

    if player > bot:
        update_sikke(user, bet)
        text = f"🎲 Sen:{player}\n🤖 Bot:{bot}\n🎉 Kazandın +{bet}"

    elif player < bot:
        update_sikke(user, -bet)
        text = f"🎲 Sen:{player}\n🤖 Bot:{bot}\n😢 Kaybettin -{bet}"

    else:
        text = "🤝 Berabere"

    await update.message.reply_text(text)


# BASKET
async def basket(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name
    sikke = get_user(user, name)

    try:
        bet = int(context.args[0])
    except:
        bet = 50

    if sikke < bet:
        await update.message.reply_text("❌ Yetersiz bakiye")
        return

    msg = await update.message.reply_dice(emoji="🏀")
    value = msg.dice.value

    if value >= 4:
        win = bet * 2
        update_sikke(user, win)
        text = f"🏀 Basket oldu +{win}"

    else:
        update_sikke(user, -bet)
        text = f"🏀 Kaçtı -{bet}"

    await update.message.reply_text(text)


# DUEL
async def duel(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Birine reply yaparak kullan\n/duel 100")
        return

    user1 = update.effective_user
    user2 = update.message.reply_to_message.from_user

    try:
        bet = int(context.args[0])
    except:
        return

    sikke1 = get_user(user1.id, user1.first_name)
    sikke2 = get_user(user2.id, user2.first_name)

    if sikke1 < bet or sikke2 < bet:
        await update.message.reply_text("❌ Bir oyuncuda yeterli para yok")
        return

    winner = random.choice([1,2])

    if winner == 1:
        update_sikke(user1.id, bet)
        update_sikke(user2.id, -bet)
        text = f"⚔️ {user1.first_name} kazandı +{bet}"

    else:
        update_sikke(user1.id, -bet)
        update_sikke(user2.id, bet)
        text = f"⚔️ {user2.first_name} kazandı +{bet}"

    await update.message.reply_text(text)


# GUNLUK
async def gunluk(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    get_user(user, name)

    reward = 500

    update_sikke(user, reward)

    await update.message.reply_text(f"🎁 Günlük ödül +{reward} 🪙")


# PARA GÖNDER
async def gonder(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply ile kullan")
        return

    sender = update.effective_user.id
    sender_name = update.effective_user.first_name
    receiver = update.message.reply_to_message.from_user.id
    receiver_name = update.message.reply_to_message.from_user.first_name

    get_user(sender, sender_name)
    get_user(receiver, receiver_name)

    try:
        amount = int(context.args[0])
    except:
        return

    update_sikke(sender, -amount)
    update_sikke(receiver, amount)

    await update.message.reply_text("💸 Para gönderildi")


# BANK
async def bank(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    get_user(user, name)

    cursor.execute("SELECT bank FROM users WHERE user_id=?", (user,))
    data = cursor.fetchone()

    bank = data[0] if data else 0

    await update.message.reply_text(f"🏦 Banka: {bank} 🪙")


# DEPOSIT
async def deposit(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    sikke = get_user(user, name)

    try:
        amount = int(context.args[0])
    except:
        return

    if sikke < amount:
        await update.message.reply_text("❌ Bakiye yok")
        return

    update_sikke(user, -amount)

    cursor.execute(
        "UPDATE users SET bank = bank + ? WHERE user_id=?",
        (amount, user)
    )
    conn.commit()

    await update.message.reply_text("🏦 Bankaya yatırıldı")


# WITHDRAW
async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    get_user(user, name)

    try:
        amount = int(context.args[0])
    except:
        return

    cursor.execute("SELECT bank FROM users WHERE user_id=?", (user,))
    data = cursor.fetchone()

    bank = data[0] if data else 0

    if bank < amount:
        await update.message.reply_text("❌ Bankada yeterli para yok")
        return

    cursor.execute(
        "UPDATE users SET bank = bank - ? WHERE user_id=?",
        (amount, user)
    )
    conn.commit()

    update_sikke(user, amount)

    await update.message.reply_text("🏦 Bankadan çekildi")


# HAFTALIK
async def haftalik(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.effective_user.id
    name = update.effective_user.first_name

    get_user(user, name)

    reward = 2000

    update_sikke(user, reward)

    await update.message.reply_text(f"🎁 Haftalık ödül +{reward} 🪙")


# STATS
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute("SELECT COUNT(*) FROM users")
    total = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(sikke) FROM users")
    money = cursor.fetchone()[0]

    await update.message.reply_text(
        f"📊 Casino İstatistik\n\n"
        f"👥 Oyuncu: {total}\n"
        f"💰 Toplam Coin: {money}"
    )


# ADMIN COIN
async def addcoin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMINS:
        return

    try:
        uid = int(context.args[0])
        amount = int(context.args[1])
    except:
        return

    update_sikke(uid, amount)

    await update.message.reply_text("✅ Coin verildi")


# TOP
async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cursor.execute(
        "SELECT username, sikke FROM users ORDER BY sikke DESC LIMIT 20"
    )

    users = cursor.fetchall()

    text = "🏆 En Zengin Oyuncular\n\n"

    for i, user in enumerate(users, start=1):
        text += f"{i}. {user[0]} — {user[1]} 🪙\n"

    await update.message.reply_text(text)


# BOT
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("rulet", rulet))
app.add_handler(CommandHandler("blackjack", blackjack))
app.add_handler(CommandHandler("poker", poker))
app.add_handler(CommandHandler("gonder", gonder))
app.add_handler(CommandHandler("bank", bank))
app.add_handler(CommandHandler("deposit", deposit))
app.add_handler(CommandHandler("withdraw", withdraw))
app.add_handler(CommandHandler("haftalik", haftalik))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("addcoin", addcoin))
app.add_handler(CommandHandler("top", top))
app.add_handler(CommandHandler("slot", slot))
app.add_handler(CommandHandler("zar", zar))
app.add_handler(CommandHandler("basket", basket))
app.add_handler(CommandHandler("duel", duel))
app.add_handler(CommandHandler("gunluk", gunluk))

print("🤖 Casino Bot Çalışıyor...")

app.run_polling(drop_pending_updates=True)