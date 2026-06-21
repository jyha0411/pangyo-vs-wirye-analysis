import pandas as pd

files = {
    "수정": "data/raw/buildings/건축물대장_jyha_20260620223946수정.csv",
    "하남": "data/raw/buildings/건축물대장_jyha_20260620223327하남.csv",
    "분당": "data/raw/buildings/건축물대장_jyha_20260620223905분당.csv",
    "송파": "data/raw/buildings/건축물대장_jyha_20260618014629송파.csv",
}

for name, path in files.items():
    df = pd.read_csv(path, encoding="utf-8", nrows=3)
    print(f"[{name}] 컬럼: {df.columns.tolist()[:12]}")
    if "주용도" in df.columns:
        print(f"  주용도 샘플: {df['주용도'].tolist()}")
    if "법정동" in df.columns:
        print(f"  법정동 샘플: {df['법정동'].tolist()}")
    print()