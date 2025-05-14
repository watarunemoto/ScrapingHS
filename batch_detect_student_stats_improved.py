
import os
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
from urllib.parse import urljoin, urlparse
import re

INPUT_DIR = "output"
OUTPUT_DIR = "student_stats_result"
os.makedirs(OUTPUT_DIR, exist_ok=True)

for filename in os.listdir(INPUT_DIR):
    if not filename.endswith("_school_info.csv"):
        continue

    input_path = os.path.join(INPUT_DIR, filename)
    prefecture = filename.replace("_school_info.csv", "")
    output_path = os.path.join(OUTPUT_DIR, f"{prefecture}_student_stats.csv")

    print(f"\n🏁 処理開始: {prefecture}")
    df = pd.read_csv(input_path)
    results = []

    for index, row in df.iterrows():
        school_name = row["高校名"]
        base_url = row["学校独自URL"]

        if pd.isna(base_url) or not base_url.startswith("http"):
            continue

        print(f"🔍 {prefecture}: {school_name}")
        student_num = "-"
        pass_num = "-"
        ratio = "-"

        try:
            res = requests.get(base_url, timeout=10)
            if res.status_code != 200:
                print(f"❌ メインページ取得失敗: {res.status_code}")
                continue

            soup = BeautifulSoup(res.content, "html.parser")
            text = soup.get_text()

            for line in text.splitlines():
                line = line.strip()
                # 生徒数
                if student_num == "-" and re.search(r"(生徒数|在校生|全校生徒)", line):
                    m = re.search(r"([0-9,]+) ?(名|人)?", line)
                    if m:
                        student_num = int(m.group(1).replace(",", ""))
                # 合格者数
                if pass_num == "-" and re.search(r"(国公立).{0,5}(合格|進学)", line):
                    m = re.search(r"([0-9,]+) ?(名|人)?", line)
                    if m:
                        pass_num = int(m.group(1).replace(",", ""))

            if isinstance(student_num, int) and isinstance(pass_num, int) and student_num > 0:
                ratio = round(pass_num / student_num, 3)
            else:
                if not isinstance(student_num, int): student_num = "-"
                if not isinstance(pass_num, int): pass_num = "-"
                ratio = "-"

            results.append((school_name, base_url, student_num, pass_num, ratio))

        except Exception as e:
            print(f"⚠️ {school_name} 例外: {e}")
            results.append((school_name, base_url, "-", "-", "-"))
            continue

        time.sleep(0.5)

    result_df = pd.DataFrame(results, columns=["高校名", "学校独自URL", "生徒数", "国公立合格者数", "合格率"])
    result_df.to_csv(output_path, index=False, encoding="utf-8-sig")
    print(f"🎉 完了: {output_path}")
