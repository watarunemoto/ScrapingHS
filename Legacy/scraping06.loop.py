import csv
import time
from urllib.parse import urlparse, parse_qs

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# ===== 設定 =====
AREA_CODE = "13"  # 東京都のエリアコード
BASE_LIST_URL = f"https://school.js88.com/scl_h/ichiran/list?area={AREA_CODE}"
OUTPUT_CSV = "school_info.csv"

# ===== Selenium初期化 =====
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

# ===== 学校一覧ページの処理 =====
print("📥 学校一覧を取得中...")
driver.get(BASE_LIST_URL)
time.sleep(2)  # ページの読み込みを待機

# 各高校の詳細ページへのリンクを抽出
school_links = set()
try:
    links = driver.find_elements(By.XPATH, '//a[contains(@href, "/scl_h/") and contains(@href, "220")]')
    for link in links:
        href = link.get_attribute("href")
        if href and "/scl_h/" in href:
            school_links.add(href.split("?")[0])
except Exception as e:
    print("高校リンクの取得に失敗:", e)

print(f"✅ {len(school_links)} 件の高校を検出しました。")

# ===== 各高校ページでの情報抽出 =====
results = []
for url in sorted(school_links):
    print(f"🔍 処理中: {url}")
    driver.get(url)
    time.sleep(1)

    school_id = url.rstrip("/").split("/")[-1]

    try:
        school_name = wait.until(EC.presence_of_element_located((By.TAG_NAME, "h1"))).text.strip()
    except:
        school_name = ""

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

    try:
        homepage_raw = wait.until(
            EC.presence_of_element_located((By.XPATH, '//dt[text()="ホームページ"]/following-sibling::dd[1]/a'))
        ).get_attribute("href")

        parsed = urlparse(homepage_raw)
        query = parse_qs(parsed.query)
        homepage = query.get("scl_url", [homepage_raw])[0]
    except:
        homepage = ""

    results.append([school_id, school_name, url, zip_code, address, homepage])

# ===== CSV書き出し（BOM付きUTF-8）=====
with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "学校名", "JS88_URL", "郵便番号", "住所", "高校ホームページ"])
    writer.writerows(results)

print(f"\n✅ 完了しました。{OUTPUT_CSV} に {len(results)} 件のデータを書き出しました。")

driver.quit()
