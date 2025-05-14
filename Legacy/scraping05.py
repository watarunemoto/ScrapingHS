import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 対象URL（1校例：札幌第一高等学校）
url = "https://school.js88.com/scl_h/22052640/"

# Chrome起動
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)
driver.get(url)

# IDの取得
school_id = url.strip("/").split("/")[-1]

# 学校名（h1）
try:
    school_name = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.strip()
except:
    school_name = ""

# 郵便番号と住所（address）
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

# 高校独自のホームページ（dt → dd → a）
try:
    homepage = wait.until(
        EC.presence_of_element_located((By.XPATH, '//dt[text()="ホームページ"]/following-sibling::dd[1]/a'))
    ).get_attribute("href")
except:
    homepage = ""

# CSV出力
with open("school_info.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "学校名", "JS88_URL", "郵便番号", "住所", "高校ホームページ"])
    writer.writerow([school_id, school_name, url, zip_code, address, homepage])

print("✅ school_info.csv を出力しました。")

driver.quit()
