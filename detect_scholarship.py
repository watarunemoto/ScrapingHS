import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time

# 入力ファイル
INPUT_CSV = "output/北海道_school_info.csv"
OUTPUT_CSV = "hokkaido_special_scholarship_flag.csv"

# キーワード
keywords = ["特待生", "特待制度", "授業料免除", "学費免除", "入学金免除"]

# 最大サブページ数
MAX_SUBPAGES = 5

# 読み込み
df = pd.read_csv(INPUT_CSV)

results = []

for index, row in df.iterrows():
    school_name = row["高校名"]
    base_url = row["学校独自URL"]

    if pd.isna(base_url) or not base_url.startswith("http"):
        continue

    print(f"🔍 処理中: {school_name} - {base_url}")
    found = False
    visited = set()

    try:
        res = requests.get(base_url, timeout=10)
        if res.status_code != 200:
            print(f"❌ メインページ取得失敗: {res.status_code}")
            continue
        soup = BeautifulSoup(res.content, "html.parser")
        text = soup.get_text()
        if any(k in text for k in keywords):
            found = True
        visited.add(base_url)

        if not found:
            links = soup.find_all("a", href=True)
            subpages = {urljoin(base_url, a["href"]) for a in links}
            count = 0
            for sub_url in subpages:
                if count >= MAX_SUBPAGES:
                    break
                if sub_url in visited:
                    continue
                if not urlparse(sub_url).netloc.endswith(urlparse(base_url).netloc):
                    continue
                try:
                    res_sub = requests.get(sub_url, timeout=10)
                    if res_sub.status_code != 200:
                        continue
                    soup_sub = BeautifulSoup(res_sub.content, "html.parser")
                    sub_text = soup_sub.get_text()
                    if any(k in sub_text for k in keywords):
                        found = True
                        break
                    visited.add(sub_url)
                    count += 1
                    time.sleep(0.5)
                except Exception as e:
                    print(f"⚠️ サブページエラー: {e}")
                    continue

        if found:
            print(f"✅ 特待制度キーワード発見: {school_name}")
            results.append((school_name, base_url))
        else:
            print(f"🚫 特待制度なし: {school_name}")

    except Exception as e:
        print(f"⚠️ {school_name} 処理エラー: {e}")
        continue

    time.sleep(0.5)

# 保存
result_df = pd.DataFrame(results, columns=["高校名", "学校独自URL"])
result_df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
print(f"🎉 出力完了: {OUTPUT_CSV}")


