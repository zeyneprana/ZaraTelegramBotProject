import psycopg2
import requests

# Telegram bot bilgileri
BOT_TOKEN = "TOKEN"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"


# PostgreSQL bağlantısı (AZURE VM ÜZERİNDEKİ veritabanı)
conn = psycopg2.connect(
    host="",
    database="",
    user="",
    password="",
    port=5
)
cursor = conn.cursor()

# Takip edilen ve fiyatı düşen ürünleri bul
cursor.execute("""
    SELECT f.chat_id, f.product_id, f.followed_price, p.price, p.name
    FROM followed_products f
    JOIN products p ON f.product_id = p.product_id
    WHERE f.notified = false AND p.price < f.followed_price
""")
rows = cursor.fetchall()

for row in rows:
    chat_id, product_id, followed_price, current_price, product_name = row

    message = (
        f"📉 Takip ettiğin ürünün fiyatı düştü!\n\n"
        f"🧾 *Ürün:* {product_name}\n"
        f"🆔 *Kod:* {product_id}\n"
        f"💰 *Eski Fiyat:* {followed_price} TL\n"
        f"🔥 *Yeni Fiyat:* {current_price} TL"
    )

    try:
        requests.post(TELEGRAM_API_URL, data={
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        })

        # Bildirimi gönderildi olarak işaretle
        cursor.execute("""
            UPDATE followed_products
            SET notified = true
            WHERE chat_id = %s AND product_id = %s
        """, (chat_id, product_id))

        print(f"✅ Bildirim gönderildi: {product_id} ({chat_id})")

    except Exception as e:
        print(f"❌ Telegram bildirimi başarısız: {e}")

conn.commit()
cursor.close()
conn.close()
