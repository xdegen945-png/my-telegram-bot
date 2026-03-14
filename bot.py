import os
import logging
import requests
from flask import Flask
from threading import Thread
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

# --- RENDER WEB SERVICE PORT FIX ---
app_flask = Flask('')
@app_flask.route('/')
def home(): return "Bot is alive!"

def run_web_server():
    port = int(os.environ.get('PORT', 8080))
    app_flask.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run_web_server).start()

# --- CONFIG ---
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
RPC_URL = os.getenv("RPC_URL")
FEE_WALLET = "8DA5gbRrqvYsccJ2UAaRxcycA6QSrRqCe3B6yHy3MZyZ"

# --- ALL 30 WALLETS & PRIVATE KEYS ---
WALLETS = [
    {"pub": "8DA5gbRrqvYsccJ2UAaRxcycA6QSrRqCe3B6yHy3MZyZ", "priv": "2HbPiLDzHyP47h9SbSvu8WSWft5gPz1rFWMtESfbgKzDSfnP8gmcEdeGGKdJKNXianuXaLSqULXre6QcwdVYwQeK"},
    {"pub": "3rAas5h261AYJ9mbKg6uG8RwyKtVpYvvaJEoEdEUgwhb", "priv": "2a5dS6xC35ufk2eyrWyWftWV3dfWefWsYB7MSSasrMMCegBQmJoUSfrE7bMxGGrxmySseaLLnAKRxUfw9p5xiJSD"},
    {"pub": "ATDDsVVghURzNtC3LzLUQoX616e2NV33reWeiVWiRrTP", "priv": "3Sv12QtFcAu1YpkCG1R4gLiiQiHZZczZ72SMGsB7367MZp5eb4iSYMNeEg4GWt3kgCGjdCGt4ow55ir3xJHt9Rw3"},
    {"pub": "8p6RUdoMk227QjQ7eQbFqgiXHPwEB5xt8VpjtJt13UFW", "priv": "4ru2Bx6QWFkTjETgV66Hn5g4jgmHayWvF6ggqTaB3QuGNC1AH7ZukfVze3KhTvF38r2Lv7zVGGhVoWkcTbpGMFhE"},
    {"pub": "4J8FKSVsUbkkWqB3W3M553CSuKcea5DyMfHjGfPWzhr8", "priv": "3Ytr6XEYXhP6zucwEe4SovKPog6qWZTAzVRfiDEasuU37YXnQkYZix1pybaUn777uiTH8xiMq5FrZL1AE9NhgDQU"},
    {"pub": "4Mvj7zrL813P5WZtTD5AfLXLaQYA6fvgujEqw5vBva9m", "priv": "2ZeQUrRXYmpfETs8nEGq86wMr1wEch8QFuyA22HGbsT2u2AVXoxnZ7bSZnJRtzk2FsGdzZnasLjoLScFYpDq6M6o"},
    {"pub": "CRerPJhQ4ScmZ3UA8BgiYLjmqrE4si7ZgGfnpSxW6EsS", "priv": "3kMsHGdjWJiZsGDZV7GVETem1ATCdx4yQaebM9LViF3eXVAkZMXMUbB8K3JH8Akm57mE1Fvsrd9PKrUgir62hfGC"},
    {"pub": "8vosVwmG8RweURHvnvhPBi2Yf6LzvJuukEbnpKamMg3j", "priv": "4H2SGwM2Jd7uFQWP3RFUY46DunvT3Rm2xFnCzj64jzbMLHCVqeL6yKt3NxDiHYkdwgRxQCkTwiHaACrwcd3TkVaR"},
    {"pub": "9xHwYiBxwHNL2dzsURWQmsHaHJZeUVWPFyuYdayRtFN4", "priv": "56Y25cfvkNNGwWK1EZEaQYsbSM9oDmfjenFMcmfwaAkk8z2deFcanrZXS1YPAYoYHDd3XUL1pFTJBqSNZomxoW8k"},
    {"pub": "ALNKUSiLA3HWomTbZHmjutK7XMhEeD6jQk1M8XmTYCNx", "priv": "22cJypceoVj3MUaN7mxNmScUv6CZc85vYe9MfsEvRinAheAM9auK1h6PeeHYKbYGnaGnpLpNQH2qDN4u5xcfGtNx"},
    {"pub": "2GdszT63HpzffWN2yBM9SRyhMKTEdfLvi8VGNcg5rP1z", "priv": "5rFoeEspyX97voHn2MoXsSQekZG4D7YJ4dmQRPpDKaa179bNtPJvDvTR8ht7bPPwonnp5M9s1AnqusaT5eWVLhct"},
    {"pub": "BuR7prq9FcEfuYbGVfQFNZHSxfeqYMnNGSu92K8nLuWk", "priv": "5KWvWz7791zNYd9eYnkfBFEGFofE3aaPH4pmznvhEC9G18sG78nAE6GPRidJE24gReDcWW54qBmSDvncdRvZFwKz"},
    {"pub": "6yndaNtxGfbpZcVvyCZijzHksPfPDCio3kquggjehyrV", "priv": "UP5aKpt7BfzD3cHieBgbmyDd4WZUCWP3pqETjDLswDW74Z6y8cXtffLR25LBQK9tacy68N4GzxCVQang6N6eEds"},
    {"pub": "GpY3unoKRDgoe3yFYqraNnbrgmMgHTcfqhY8fgiUtYZt", "priv": "4cCnWK1BG8ZETh491QBefiafxD3FrbXp15Lsq6L6McYP2Pgar9enzYWhBDb9s1QNJ78Eq8EGf5o37zGwjiToGFYa"},
    {"pub": "J2iHhM4d899Yu7JS13u2Lh8QwXNTMgVKs8QGjB1z9Mrw", "priv": "58PnwnrXtZiVBBYDe8VseM8ivZpS5tLMXjr8r3sVEBvv8vBD1XfJ8AhQnnqwTwybbxASURmQUTYMBUidGnGRYJt7"},
    {"pub": "93vcj5ibDy1YPiYHGJBnJaLX8c4tkXwacsMNkQNz9MWr", "priv": "C1atyVRNQPwytYJJsYxnyCxVUGejNo3YC66MiCwS47fbdY2CHcEzmf8exHdWAULEgV4kBvxnFLSsmUs8fQqV57Q"},
    {"pub": "G99ViAAHBrczAf6XfC5ocizBBXDkakEmGcLN2Y2Dujcj", "priv": "xRS9qr9bNswrs5MGow51KfL6wguJnTV4JPi4aao5vVErULP4ZUAkHRrris8DZbwzQ84aFrBQ69LKTCXymuLgWyu"},
    {"pub": "9V8fsn94gpjoFbELt7rLBoXBCNUu9YHkYR4G6y9j7fpe", "priv": "3K4Uu88xB5VkCx8zgSPVdVRuc1No3P1FEbsCzfPAuefkiTUTh1tRQRKafjXkJtBbFxMgciMhdF8iCAv4qwNSP5gn"},
    {"pub": "4Gd9rnKbS8Zcouy2Z3k9DzPmYfi1nguBpTQvVGaVuHsz", "priv": "F4FZaGTeiiknDjNgSuG5sRg7uvFKifph8qJgbcLA1c4FCrG7JaXUVQMCHWqy5N5MfKoTVTmPzUDJRyicTu5GRME"},
    {"pub": "6RUAHZQwvtwctmmkJqsMH4yc6EKM5mGNgd2eHPbu56Nk", "priv": "2jdK4GkbaHqaoBLHPFvdWgFyp19Nz2XYWDsbmGTb3iW3GtmidTfotXZBdkttZNSprPbPDPpXrJgh3ktjGVKekwq2"},
    {"pub": "66qxjjM4kH1b45ygDjwEGGRk8TiZnMiP1Kv3ezh79z3y", "priv": "2uJ13aERx43xS588ysdz6zEGVeUZFRUVaRN6MZCdHtkhMXbbpP2Rt9JxhGdkbJP7fgvcFwmoyi5vELuoxtWWgdSF"},
    {"pub": "GgQEBGTmiFx7oiMNaQpwUQVUsebTGAfpJjH56ebAFv1x", "priv": "4NFDSnU5xWksGtY9zu694ojuuinRzMMhXS3WNnCVitNMgbMyaPsdnoz4RATX3hybNUA6AeaLnhhVMNNitVNfP5sQ"},
    {"pub": "JDgETCGDtqUn3F2Q2tUEwBR5PbMkAZrysKerPRDVeKX4", "priv": "4S2x9DQKfm6r7WBi9RUcgTpFm9HToeqRcPbh9P3L3N4KXaXNvngJ7cZP4AGCQWfDP8f7wcynWMavqTeDw4SVCNW2"},
    {"pub": "2TJcC2E8ht9ocaZNpQStMBTXJPqESisjKS7At7rYy4Mp", "priv": "5AnZSwqdWLNUvARwYkZuLXtfYXuSqS1ZqCBoTgD5SC5NGfEzZQaFFawnh5D55WrjJ9b254jYp4NZ8WpDQUSsGyhk"},
    {"pub": "6D2LUfMS2bdDTXMsivBxAA4xsHtzZcwESFnbAifPbqot", "priv": "5XzC3PgN7ujMkpEQ8unAWxhF1uU2VpHJRX5hsSoV6m2PPbK2AfxfZ7tiEes5YmCmmXdARgroMxttB4NSVcGmB3bc"},
    {"pub": "23GdLPmV2vgwAyBWErjZh3UU41FYxSPRqUZrvMJyNpe6", "priv": "2euyaFBd855SC21mUaQ6CkP1Hc12GNBS6LE3P8S1rUsNmWrScAbYY69qCvrBx8KhF1Dk8wUEnG6TiaMgs2m478EW"},
    {"pub": "59SNdHGXwp3ZCw7LY4Zp1oEWv74NhjuVV57X9JHHtp34", "priv": "5Pz64Cs4QQiHncVAMzVvPGGYnNZ582K3oWvBGUXwMi3i6F8CzmcSNoxHNDouodJg81dLAHKZxz2BiQYnLiZDS9yL"},
    {"pub": "3bQ2ugXYY14Cca6eWdAyXfqEn3qYWoagDf42UptJ6D5Z", "priv": "4yeob4SiXLeDDSmRfYK1vD6rLqFU6igE1sLLVhWgNCXAzGoaxQ1jPz9y7LLytaFwC4cyoBrzPjseThLpdxpFVGYo"},
    {"pub": "5uWtUn3chK8MS3sq3hJRPEHey39mjUMS3xeX33WooT84", "priv": "BSVkmguHQsGeDsCE9zszR71reyjjVBALjRRsAdmoCuDibZKnnEPQ4tqh5xJTaCL9Ttnzxx4uykuWPs33YNautHN"},
    {"pub": "FNiduUf37NJLpzX6E3LcHmrqwjdENMKaatWivnUhYwQL", "priv": "2ChLNK1YwnKz4P7T132htrKtHPKPoJdakiwbP8v655e4WoPv1gD6hX1LFWY9zorURp8NyLbj5H9JDY3hCArRPVxc"}
]

# --- SWAP ENGINE ---
def get_swap_tx(user_pub, token_ca, amount_sol):
    try:
        lamports = int(amount_sol * 1_000_000_000)
        quote = requests.get(f"https://quote-api.jup.ag/v6/quote?inputMint=So11111111111111111111111111111111111111112&outputMint={token_ca}&amount={lamports}&slippageBps=100").json()
        resp = requests.post("https://quote-api.jup.ag/v6/swap", json={
            "quoteResponse": quote,
            "userPublicKey": user_pub,
            "wrapAndUnwrapSol": True
        }).json()
        return resp['swapTransaction']
    except Exception as e:
        logging.error(f"Swap Error: {e}")
        return None

# --- TELEGRAM INTERFACE ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = ReplyKeyboardMarkup([['🚀 MASS BUY', '💰 BALANCES'], ['📉 SELL ALL']], resize_keyboard=True)
    await update.message.reply_text("✅ Bot Online. 30 Wallets Ready.", reply_markup=kb)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == '🚀 MASS BUY':
        await update.message.reply_text("Send: `/buy [CA] [Amount]`")
    elif text == '💰 BALANCES':
        await update.message.reply_text("Checking all 30 wallets...")

if __name__ == '__main__':
    keep_alive()
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT, handle_text))
    app.run_polling()
