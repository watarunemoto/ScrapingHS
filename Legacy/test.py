import pandas as pd

df = pd.read_csv("all_pref_schools.csv")
print(df["都道府県"].value_counts())


import os

pref_all = set(pd.read_csv("all_pref_schools.csv")["都道府県"].unique())
pref_done = {f.replace("_school_info.csv", "") for f in os.listdir("output") if f.endswith("_school_info.csv")}
missing = sorted(pref_all - pref_done)

print("🔍 未処理の都道府県：", missing)
