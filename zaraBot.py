from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import psycopg2
import re
import ast  

TOKEN = "token"

conn = psycopg2.connect(
    host="",
    database="",
    user="",
    password="",
    port=5
)
cursor = conn.cursor()

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Merhaba! Zara ürün linkini gönder, sana ürün bilgilerini ve tüm resimlerini vereyim.")

async def handle_product_link(update: Update, context: CallbackContext):
    product_url = update.message.text.strip()

    match = re.search(r'p\d{8}', product_url)
    if not match:
        await update.message.reply_text("Geçerli bir Zara ürün linki gönderin.")
        return

    product_code = match.group()
    try:
        cursor.execute("""
            SELECT name, price, colour, description, code, image_url, extra_images
            FROM products
            WHERE url ILIKE %s
        """, ('%' + product_code + '%',))
        result = cursor.fetchone()
    except Exception:
        await update.message.reply_text("Veritabanında arama yapılırken bir hata oluştu.")
        return

    if not result:
        await update.message.reply_text("Bu linkle eşleşen bir ürün bulunamadı.")
        return

    name, price, colour, description, code, picture, extra_pictures = result

    # extra_pictures Postgres text[] tipi olduğu için Python listesine doğrudan dönüşüyor,
    # ama bazen string olarak gelebilir, kontrol edip parse edelim:
    if isinstance(extra_pictures, str):
        try:
            extra_pictures = ast.literal_eval(extra_pictures)
        except:
            extra_pictures = []

    msg = (
        f"\U0001F457 *Ürün:* {name}\n"
        f"\U0001F4B8 *Fiyat:* {price} TL\n"
        f"\U0001F3A8 *Renk:* {colour}\n"
        f"\U0001F4DD *Açıklama:* {description}\n"
        f"\U0001F194 *Kod:* {code}"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

    if picture and picture != "YOK":
        await update.message.reply_photo(photo=picture)

    try:
        for img in extra_pictures:
            if img and img != "YOK":
                await update.message.reply_photo(photo=img)
    except:
        pass

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_link))

print("Bot products tablosu ile çalışıyor...")
app.run_polling()
