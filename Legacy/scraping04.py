import csv
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 対象URL（例：札幌第一高等学校）
url = "https://school.js88.com/scl_h/22052640/"

# Chrome起動設定
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

driver.get(url)

# 1列目: ID
school_id = url.strip("/").split("/")[-1]

# 2列目: 高等学校名（<h1>タグ）
try:
    school_name = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.strip()
except:
    school_name = ""

# 3列目: URL（元のURLそのまま）
school_url = url

# 4列目 & 5列目: 郵便番号と住所（<address>）
try:
    address_full = wait.until(EC.presence_of_element_located((By.TAG_NAME, "address"))).text.strip()
    if "〒" in address_full:
        zip_code = address_full.split()[0].replace("〒", "")
        address = address_full.replace(f"〒{zip_code}", "").strip()
    else:
        zip_code = ""
        address = address_full
except:
    zip_code = ""
    address = ""

# 結果をCSV形式で保存
with open("school_info.csv", "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["ID", "学校名", "URL", "郵便番号", "住所"])  # ヘッダー
    writer.writerow([school_id, school_name, school_url, zip_code, address])

print("✅ school_info.csv を出力しました。")

driver.quit()
