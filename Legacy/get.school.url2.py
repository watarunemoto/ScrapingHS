import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# 千葉県に絞る
df = pd.read_csv("all_pref_schools.csv")
df = df[df["都道府県"] == "千葉県"]

detailed_data = []

for index, row in df.iterrows():
    pref, school_name, url = row["都道府県"], row["高校名"], row["高校ページURL"]
    try:
        res = requests.get(url)
        if res.status_code != 200:
            continue
        soup = BeautifulSoup(res.content, "html.parser")

        # 郵便番号と住所
        address_tag = soup.find("address")
        postal_code, address = "", ""
        if address_tag:
            full_address = address_tag.text.strip().replace("\u3000", " ").replace("\xa0", " ")
            if full_address.startswith("〒"):
                postal_code = full_address.split(" ")[0].replace("〒", "")
                address = full_address[len(postal_code) + 2:].strip()

        # 独自URL
        school_url = ""
        dt_tags = soup.find_all("dt")
        for dt in dt_tags:
            if "ホームページ" in dt.text:
                dd = dt.find_next_sibling("dd")
                if dd and dd.a:
                    school_url = dd.a.get("href")
                    if "scl_url=" in school_url:
                        school_url = school_url.split("scl_url=")[-1]
                break

        detailed_data.append((pref, school_name, url, postal_code, address, school_url))

    except Exception as e:
        print(f"⚠️ {school_name} でエラー: {e}")
    time.sleep(0.5)

# 出力
output_df = pd.DataFrame(detailed_data, columns=["都道府県", "高校名", "高校ページURL", "郵便番号", "住所", "学校独自URL"])
output_df.to_csv("chiba_school_info.csv", index=False, encoding="utf-8-sig")
