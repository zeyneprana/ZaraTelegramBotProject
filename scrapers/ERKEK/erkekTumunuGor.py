from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
import psycopg2
from erkekMain import erkekButton

productDict = {
    'picture': [],
    'extra_pictures': [],
    'name': [],
    'price': [],
    'colour': [],
    'code': [],
    'description': [],
    'product_url': []
}

driver = erkekButton()
sleep(3)

# ELBİSE kategorisine tıkla
driver.find_element(By.XPATH, '//span[@class="layout-categories-category__name" and text()="TÜMÜNÜ GÖR"]').click()

# Yeni sekmeye geç
if len(driver.window_handles) > 1:
    driver.switch_to.window(driver.window_handles[-1])

# Sonsuz scroll
lastHeight = driver.execute_script("return document.body.scrollHeight")
while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(1)
    newHeight = driver.execute_script("return document.body.scrollHeight")
    if newHeight == lastHeight:
        break
    lastHeight = newHeight

# Ürün linklerini topla
product_links = set()
products = driver.find_elements(By.CSS_SELECTOR, 'a.product-link')
for product in products:
    link = product.get_attribute('href')
    if link:
        product_links.add(link)

product_links = list(product_links)
print(f"Eşsiz ürün linki sayısı: {len(product_links)}")

# İlk 3 ürünün detaylarını al
for link in product_links[:3]:
    driver.get(link)
    sleep(2)

    productDict['product_url'].append(link)
    print("Ürün URL:", link)

    try:
        name = driver.find_element(By.CLASS_NAME, 'product-detail-info__header-name').text
    except:
        name = "YOK"
    productDict['name'].append(name)
    print("Ürün:", name)

    try:
        price_raw = driver.find_element(By.CLASS_NAME, 'money-amount__main').text
        price_cleaned = price_raw.replace("TL", "").replace("₺", "").replace(".", "").replace(",", ".").strip()
        price = float(price_cleaned)
    except:
        price = 0.0
    productDict['price'].append(price)
    print("Fiyat:", price)

    try:
        colour = driver.find_element(By.CLASS_NAME, 'product-color-extended-name').text.split('|')[0].strip()
    except:
        colour = "YOK"
    productDict['colour'].append(colour)
    print("Renk:", colour)

    try:
        description = driver.find_element(By.CLASS_NAME, 'expandable-text__inner-content').text
    except:
        description = "YOK"
    productDict['description'].append(description)
    print("Açıklama:", description)

    try:
        code = driver.find_element(By.CLASS_NAME, 'product-color-extended-name__copy-action').text
    except:
        code = "YOK"
    productDict['code'].append(code)
    print("Kod:", code)

    try:
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'img.media-image__image')
        main_image = ""
        extra_images = []

        for index, img in enumerate(image_elements):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", img)
                sleep(0.5)
                src = img.get_attribute('src')
                if src and src.startswith('http') and ('.jpg' in src or '.jpeg' in src or '.png' in src):
                    if index == 0:
                        main_image = src
                    else:
                        extra_images.append(src)
            except:
                continue

        productDict['picture'].append(main_image if main_image else "YOK")
        productDict['extra_pictures'].append(extra_images if extra_images else [])
        print("Ana Resim:", main_image)
        print("Ekstra Resimler:", extra_images)
    except:
        productDict['picture'].append("YOK")
        productDict['extra_pictures'].append([])
        print("Resimler: YOK")

    print("--------")

# PostgreSQL'e kaydet veya güncelle
def save_to_postgresql(productDict):
    conn = psycopg2.connect(
        host="",
        database="",
        user="",
        password="",
        port=5
    )
    cursor = conn.cursor()

    for i in range(len(productDict['name'])):
        try:
            cursor.execute("""
                INSERT INTO products (
                    product_id, name, price, colour, code, description,
                    url, image_url, extra_images, category
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (product_id) DO UPDATE SET
                    name = EXCLUDED.name,
                    price = EXCLUDED.price,
                    colour = EXCLUDED.colour,
                    description = EXCLUDED.description,
                    url = EXCLUDED.url,
                    image_url = EXCLUDED.image_url,
                    extra_images = EXCLUDED.extra_images,
                    last_updated = CURRENT_TIMESTAMP
            """, (
                productDict['code'][i],
                productDict['name'][i],
                productDict['price'][i],
                productDict['colour'][i],
                productDict['code'][i],
                productDict['description'][i],
                productDict['product_url'][i],
                productDict['picture'][i],
                productDict['extra_pictures'][i],
                "Erkek > Tümünü Gör"
            ))
        except Exception as e:
            print(f"Hata oluştu: {e}")

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ Tüm ürünler PostgreSQL veritabanına kaydedildi.")

# Çalıştır
save_to_postgresql(productDict)


