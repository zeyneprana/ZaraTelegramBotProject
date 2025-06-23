from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import psycopg2
import re
import ast

# Telegram Bot Token
TOKEN = "TOKEN"

# PostgreSQL bağlantısı
conn = psycopg2.connect(
    host="",
    database="",
    user="",
    password="",
    port=5
)
cursor = conn.cursor()

# Başlat komutu
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Merhaba! Zara ürün linkini gönder, sana ürün bilgilerini ve tüm resimlerini vereyim.\nTakip için: /follow <zara linki>")

# Ürün linki geldiğinde çalışır
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


#Takip fonksiyonu follow
async def follow(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Lütfen bir Zara ürün linki gönder: /follow <link>")
        return

    product_url = context.args[0]

    # Zara linkinden 8 haneli ürün kodunu çekiyoruz (p06861441)
    match = re.search(r'p(\d{8})', product_url)
    if not match:
        await update.message.reply_text("Geçerli bir Zara ürün linki gönderin.")
        return

    product_code = match.group(1)  # "06861441"
    chat_id = str(update.message.chat_id)

    try:
        # URL'den ürün kodunu bul, oradan product_id ve price al
        cursor.execute("""
            SELECT product_id, price FROM products
            WHERE url ILIKE %s
        """, (f'%{product_code}%',))
        result = cursor.fetchone()

        if not result:
            await update.message.reply_text("Bu ürün veritabanında bulunamadı.")
            return

        product_id, current_price = result

        # Zaten takip ediliyor mu?
        cursor.execute("""
            SELECT 1 FROM followed_products
            WHERE chat_id = %s AND product_id = %s
        """, (chat_id, product_id))
        if cursor.fetchone():
            await update.message.reply_text("Bu ürünü zaten takip ediyorsunuz.")
            return

        # Takibe ekle
        cursor.execute("""
            INSERT INTO followed_products (chat_id, product_id, followed_price)
            VALUES (%s, %s, %s)
        """, (chat_id, product_id, current_price))
        conn.commit()

        await update.message.reply_text(
            f"✅ Takip başladı!\nÜrün kodu: {product_id}\nŞu anki fiyat: {current_price} TL\n"
            f"Fiyat düşünce sana haber vereceğim 😊"
        )

    except Exception as e:
        await update.message.reply_text("Takip sırasında bir hata oluştu.")
        print(f"/follow hatası: {e}")



# Botu başlat
app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("follow", follow))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_product_link))

print("Bot çalışıyor... ürün bilgilerini ve takipleri yönetiyor.")
app.run_polling()
