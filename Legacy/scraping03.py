from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

url = "https://school.js88.com/scl_h/22052640/"
driver.get(url)

# 所在地の取得：<address> タグを使う
try:
    address = wait.until(
        EC.presence_of_element_located((By.TAG_NAME, "address"))
    ).text.strip()
except Exception as e:
    address = None
    print("所在地の取得失敗:", e)

# ホームページURLの取得：<dt>が「ホームページ」の次の<dd>内の<a>
try:
    homepage = wait.until(
        EC.presence_of_element_located((
            By.XPATH, '//dt[text()="ホームページ"]/following-sibling::dd[1]/a'
        ))
    ).get_attribute("href")
except Exception as e:
    homepage = None
    print("ホームページURLの取得失敗:", e)

# 結果出力
print("所在地:", address)
print("ホームページ:", homepage)

driver.quit()
