import csv
import time
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 全国の (big_area, area) 対応表
prefectures = [
    (1, 1),  (2, 2),  (2, 3),  (2, 4),  (2, 5),  (2, 6),  (2, 7)
]
'''
prefectures = [
    (1, 1),  (2, 2),  (2, 3),  (2, 4),  (2, 5),  (2, 6),  (2, 7),
    (3, 8),  (3, 9),  (3, 10), (3, 11), (3, 12), (3, 13), (3, 14),
    (4, 15), (4, 19), (4, 20), (4, 21), (4, 22), (4, 23), (4, 24),
    (5, 16), (5, 17), (5, 18),
    (6, 25), (6, 26), (6, 27), (6, 28), (6, 29), (6, 30),
    (7, 31), (7, 32), (7, 33), (7, 34), (7, 35),
    (8, 36), (8, 37), (8, 38), (8, 39),
    (9, 40), (9, 41), (9, 42), (9, 43), (9, 44), (9, 45), (9, 46), (9, 47)
]
'''
base_url = "https://school.js88.com/kodawari?type=22"

# セットアップ
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
wait = WebDriverWait(driver, 10)

all_school_urls = set()

print("📥 高校一覧URLを収集中...")
for big_area, area in prefectures:
    page = 1
    while True:
        url = f"{base_url}&big_area={big_area}&area={area}&page={page}"
        print(url)
        print(f"📦 {area}（{big_area}）ページ {page} を取得中...")  # ← この行を追加
        driver.get(url)
        time.sleep(1)
        links = driver.find_elements(By.XPATH, '//a[contains(@href, "/scl_h/")]')
        new_links = set()
        for link in links:
            href = link.get_attribute("href")
            if href and "/scl_h/" in href and "kodawari" not in href:
                school_id = href.split("/scl_h/")[1].split("/")[0]
                full_url = f"https://school.js88.com/scl_h/{school_id}/"
                new_links.add(full_url)
        if not new_links:
            break
        all_school_urls.update(new_links)
        page += 1

print(f"✅ 高校URL取得完了（{len(all_school_urls)}校）")

# 各高校の詳細情報取得
results = []
for idx, url in enumerate(sorted(all_school_urls), start=1):
    print(f"🔍 [{idx}/{len(all_school_urls)}] {url}")
    driver.get(url)
    time.sleep(0.5)

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

# CSV出力
with open("school_info.csv", "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["ID", "学校名", "JS88_URL", "郵便番号", "住所", "高校ホームページ"])
    writer.writerows(results)

print(f"\n✅ 完了：{len(results)} 件を school_info.csv に保存しました。")

driver.quit()
