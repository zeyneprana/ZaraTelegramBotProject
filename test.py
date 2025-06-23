
# PostgreSql Bağlantı test

import psycopg2

try:
    conn = psycopg2.connect(
        host="",
        database="",
        user="",
        password="",
        port=5432 
    )
    print("✅ Bağlantı başarılı!")
    conn.close()
except Exception as e:
    print("❌ Bağlantı başarısız:")
    print(e)          