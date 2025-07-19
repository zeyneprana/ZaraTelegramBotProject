from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep

def erkekButton():
    options = webdriver.ChromeOptions()


    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')

    # Masaüstü user-agent
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
        '(KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
    )

    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    driver.implicitly_wait(3)

    driver.get('https://www.zara.com/tr')
    sleep(2)

    try:
        accept_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-accept-btn-handler")))
        accept_btn.click()
        print("✅ Çerezler kabul edildi.")
    except Exception as e:
        print(f"⚠️ Çerez butonu yok: {e}")

    try:
        menu_icon = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "layout-header-icon__icon")))
        menu_icon.click()
        print("✅ Menü açıldı.")
        sleep(2)
    except Exception as e:
        print(f"❌ Menü açılamadı: {e}")
        driver.save_screenshot("/tmp/menu_hatasi.png")

    try:
        erkek_btn = wait.until(EC.element_to_be_clickable((By.XPATH, '//span[text()="ERKEK"]')))
        erkek_btn.click()
        print("✅ ERKEK kategorisi açıldı.")
        sleep(2)
    except Exception as e:
        print(f"❌ ERKEK kategorisi açılamadı: {e}")
        driver.save_screenshot("/tmp/erkek_kategori_hatasi.png")

    return driver

