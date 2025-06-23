
# PostgreSql Bağlantı test

import psycopg2

try:
    conn = psycopg2.connect(
        host="",  # ← Azure VM'in IP adresi
        database="",
        user="",
        password="",
        port=5
    )
    print("✅ Bağlantı başarılı!")
    conn.close()
except Exception as e:
    print("❌ Bağlantı başarısız:")
    print(e)          