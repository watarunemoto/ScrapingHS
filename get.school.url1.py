import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

prefecture_table = [
    (1, 1, "北海道"),
    (2, 2, "青森県"), (2, 3, "岩手県"), (2, 4, "宮城県"), (2, 5, "秋田県"), (2, 6, "山形県"), (2, 7, "福島県"),
    (3, 8, "茨城県"), (3, 9, "栃木県"), (3, 10, "群馬県"), (3, 11, "埼玉県"), (3, 12, "千葉県"), (3, 13, "東京都"), (3, 14, "神奈川県"),
    (4, 15, "新潟県"), (4, 19, "山梨県"), (4, 20, "長野県"),
    (5, 21, "岐阜県"), (5, 22, "静岡県"), (5, 23, "愛知県"), (5, 24, "三重県"),
    (6, 16, "富山県"),(6, 17, "石川県"), (6, 18, "福井県"),
    (7, 25, "滋賀県"), (7, 26, "京都府"), (7, 27, "大阪府"), (7, 28, "兵庫県"), (7, 29, "奈良県"), (7, 30, "和歌山県"),
    (8, 31, "鳥取県"), (8, 32, "島根県"), (8, 33, "岡山県"), (8, 34, "広島県"), (8, 35, "山口県"), (8, 36, "徳島県"), (8, 37, "香川県"), (8, 38, "愛媛県"), (8, 39, "高知県"),
    (9, 40, "福岡県"), (9, 41, "佐賀県"), (9, 42, "長崎県"), (9, 43, "熊本県"), (9, 44, "大分県"), (9, 45, "宮崎県"), (9, 46, "鹿児島県"), (9, 47, "沖縄県")
]

school_data = []

for big_area, area, pref_name in prefecture_table:
    page = 1
    while True:
        url = f"https://school.js88.com/kodawari?big-area={big_area}&area={area}&type=22&s={page}"
        res = requests.get(url)
        if res.status_code != 200:
            break
        soup = BeautifulSoup(res.content, "html.parser")
        school_blocks = soup.select("div.scl_name > h2 > a")
        if not school_blocks:
            break
        for a in school_blocks:
            school_name = a.text.strip()
            href = a.get("href")
            full_url = f"https://school.js88.com{href}"
            school_data.append((pref_name, school_name, full_url))
        print(f"✅ {pref_name} ページ {page}：{len(school_blocks)} 件")
        page += 1
        time.sleep(0.5)

df = pd.DataFrame(school_data, columns=["都道府県", "高校名", "高校ページURL"])
df.to_csv("all_pref_schools.csv", index=False, encoding="utf-8-sig")
print("🎉 完了：all_pref_schools.csv に保存しました。")



'''
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd

big_area = 3
area = 12
pref_name = "千葉県"

school_data = []
page = 1

while True:
    url = f"https://school.js88.com/kodawari?big-area={big_area}&area={area}&type=22&s={page}"
    res = requests.get(url)
    if res.status_code != 200:
        break

    soup = BeautifulSoup(res.content, "html.parser")
    school_blocks = soup.select("div.scl_name > h2 > a")
    if not school_blocks:
        break

    for a in school_blocks:
        school_name = a.text.strip()
        href = a.get("href")
        full_url = f"https://school.js88.com{href}"
        school_data.append((pref_name, school_name, full_url))

    print(f"✅ {pref_name} ページ {page}：{len(school_blocks)} 件")
    page += 1
    time.sleep(0.5)

df = pd.DataFrame(school_data, columns=["都道府県", "高校名", "高校ページURL"])
df.to_csv("chiba_schools.csv", index=False, encoding="utf-8-sig")
print("🎉 完了：chiba_schools.csv に保存しました。")
'''
