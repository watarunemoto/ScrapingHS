import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from collections import Counter

INPUT_DIR = "output"
OUTPUT_DIR = "scholarship_result"
LOG_DIR = "logs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(LOG_DIR, exist_ok=True)

keywords = ["特待生", "特待制度", "授業料免除", "学費免除", "入学金免除"]
MAX_SUBPAGES = 10
total_keyword_counter = Counter()

def log_write(logfile, message):
    print(message)
    logfile.write(message + "\n")

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith("_school_info.csv"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    prefecture = filename.replace("_school_info.csv", "")
    output_path = os.path.join(OUTPUT_DIR, f"{prefecture}_special_scholarship_flag.csv")
    log_path = os.path.join(LOG_DIR, f"{prefecture}.log")

    with open(log_path, "w", encoding="utf-8") as log:
        log_write(log, f"\n🏁 処理開始: {prefecture}")
        df = pd.read_csv(input_path)
        results = []
        keyword_counter = Counter()

        for index, row in df.iterrows():
            school_name = row["高校名"]
            base_url = row["学校独自URL"]

            if pd.isna(base_url) or not base_url.startswith("http"):
                continue

            log_write(log, f"🔍 {school_name} - {base_url}")
            found = False
            visited = set()

            try:
                res = requests.get(base_url, timeout=10)
                if res.status_code != 200:
                    log_write(log, f"❌ メインページ取得失敗: {res.status_code}")
                    continue
                soup = BeautifulSoup(res.content, "html.parser")
                text = soup.get_text()
                for kw in keywords:
                    if kw in text:
                        keyword_counter[kw] += 1
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
                            for kw in keywords:
                                if kw in sub_text:
                                    keyword_counter[kw] += 1
                                    found = True
                            visited.add(sub_url)
                            count += 1
                            time.sleep(0.5)
                        except Exception as e:
                            log_write(log, f"⚠️ サブページエラー: {e}")
                            continue

                if found:
                    log_write(log, f"✅ 特待制度あり: {school_name}")
                    results.append((school_name, base_url))
                else:
                    log_write(log, f"🚫 特待制度なし: {school_name}")

            except Exception as e:
                log_write(log, f"⚠️ {school_name} 例外: {e}")
                continue

            time.sleep(0.5)

        # 保存
        result_df = pd.DataFrame(results, columns=["高校名", "学校独自URL"])
        result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
        log_write(log, f"🎉 完了: {output_path}")

        # 都道府県別キーワード頻度を集約
        for k, v in keyword_counter.items():
            total_keyword_counter[(prefecture, k)] = v



# 全体のキーワード統計を保存
stats_rows = [{"都道府県": pref, "キーワード": kw, "件数": count}
              for (pref, kw), count in total_keyword_counter.items()]
stats_df = pd.DataFrame(stats_rows)
stats_df.to_csv("keyword_stats.csv", index=False, encoding="utf-8-sig")
print("📊 キーワード頻度を keyword_stats.csv に保存しました。")

