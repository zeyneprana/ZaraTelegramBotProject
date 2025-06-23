from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep


def erkekButton():
    # Tarayıcı ayarları
    options = webdriver.ChromeOptions()
    options.add_experimental_option('detach', True)
    options.add_argument('--start-maximized')

    driver = webdriver.Chrome(options=options)
    actions = ActionChains(driver)
    driver.implicitly_wait(3)

    # Siteye git
    driver.get('https://www.zara.com/tr')
    sleep(1)
    
    # Çerezleri kabul et
    driver.find_element(By.ID, "onetrust-accept-btn-handler").click()
    sleep(1)

    # Menüden ERKEK'i seç
    driver.find_element(By.CLASS_NAME, "layout-header-icon__icon").click()
    sleep(1)
    driver.find_element(By.XPATH, '//span[@class="layout-categories-category__name" and text()="ERKEK"]').click()
    sleep(1)

    return driver