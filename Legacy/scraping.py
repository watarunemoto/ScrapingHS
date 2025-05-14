from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import re


base_url = "https://school.js88.com/kodawari?type=22"

# `big-area` と `area` の対応表
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
prefectures = [
    (1, 1),  (2, 2)
]
    
# Seleniumのセットアップ
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # GUIなしで実行
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)



# 高校の詳細ページURLを作成する関数
def create_school_url(school_id):
    return f"https://school.js88.com/scl_h/{school_id}/"

# 高校名・FAX番号・ホームページ情報を取得する関数
def get_school_info(driver, school_id):
    url = create_school_url(school_id)
    driver.get(url)
    
    time.sleep(3)  # ページの読み込みを待つ

    school_name = "未取得"
    fax_number = "未取得"
    homepage_url = "未取得"

    # ページのHTMLを取得
    page_source = driver.page_source

    try:
        # 高校名を取得
        school_name_element = driver.find_element(By.XPATH, "//h1[contains(@class, 'scl-name')]")
        school_name = school_name_element.text.strip() if school_name_element else "未取得"

        # FAX番号を正規表現で抽出
        fax_match = re.search(r'FAX\.(\d{2,4}-\d{2,4}-\d{4})', page_source)
        if fax_match:
            fax_number = fax_match.group(1)

        # ホームページURLを取得
        homepage_element = driver.find_element(By.XPATH, "//dt[contains(text(), 'ホームページ')]/following-sibling::dd/a")
        redirect_url = homepage_element.get_attribute("href") if homepage_element else "未取得"

        # `scl_url=` 以降のURLを抽出
        if redirect_url and "scl_url=" in redirect_url:
            homepage_match = re.search(r'scl_url=(https?://[^\s&]+)', redirect_url)
            if homepage_match:
                homepage_url = homepage_match.group(1)
                
    except Exception as e:
        print(f"エラー: {e}")
        
    return school_name, fax_number, homepage_url




# 取得済みの高校IDリスト（テスト用）
#school_ids = ["34028395", "22050590", "22050678"]  # 追加で複数の学校をテスト


# ファイルに保存
output_file = "school_data.txt"

# 出力ファイルを開く
with open(output_file, "w", encoding="utf-8") as f:
#with open("school_ids.txt", "w") as f:
    f.write("高校ID\t高校名\tURL\tFAX番号\tホームページURL\n")  # ヘッダー行を追加
    for big_area, area in prefectures:
        url = f"{base_url}&big-area={big_area}&area={area}"
        print(f"アクセス中: {url}")
        driver.get(url)

        try:
            # 高校一覧が表示されるまで待機
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/scl_h/')]"))
            )
            time.sleep(2)  # JavaScriptの実行を待つ

            # 高校の詳細ページのリンクを取得
            links = driver.find_elements(By.XPATH, "//a[contains(@href, '/scl_h/')]")

            visited_ids = set()  # IDの重複を避けるためのセット

            for link in links:
                href = link.get_attribute("href")
                school_name = link.text.strip()

                # IDを抽出
                match = re.search(r"/scl_h/(\d+)", href)
                if match:
                    school_id = match.group(1)

                    # 既に取得済みのIDでなければ保存
                    if school_id not in visited_ids and school_name and "学校情報を見る" not in school_name:
                        visited_ids.add(school_id)

                        # ファイルに即時書き込み
                        f.write(f"{school_id}\t{school_name}\n")
                        f.flush()  # 書き込みを即時反映

                        print(f"取得: {school_id} - {school_name}")

                        #    for school_id in school_ids:
                        school_name, fax, homepage = get_school_info(driver, school_id)
                        line = f"{school_id}\t{school_name}\t{create_school_url(school_id)}\t{fax}\t{homepage}\n"
                        print(line.strip())  # コンソールにも出力
                        f.write(line)

                                               
            print(f"累計取得高校数: {len(visited_ids)}")

        except Exception as e:
            print(f"エラー: {e}")

            
driver.quit()

print(f"\nデータを '{output_file}' に保存しました。")




