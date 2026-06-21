import pandas as pd
import os

# 집계구코드 앞 5자리 = 시군구코드
# 11240=송파, 31021=분당, 31023=수정, 31180=하남
REGION_MAP = {
    "11240": "송파(위례)",
    "31021": "분당(판교)",
    "31023": "수정(위례)",
    "31180": "하남(위례)",
}

census_dir = "data/raw/census"
os.makedirs("data/processed", exist_ok=True)

all_dfs = []

for fname in os.listdir(census_dir):
    if not fname.endswith(".csv"):
        continue

    fpath = os.path.join(census_dir, fname)
    df = pd.read_csv(fpath, encoding="utf-8", header=None)
    df.columns = ["year", "census_code", "indicator", "value"]

    # 지역코드 추출 (앞 5자리)
    df["sigungu"] = df["census_code"].astype(str).str[:5]
    df["region"] = df["sigungu"].map(REGION_MAP)

    # 파일명에서 지표명 추출
    name = fname.replace(".csv", "")
    df["source_file"] = name

    all_dfs.append(df)

merged = pd.concat(all_dfs, ignore_index=True)

# 주요 지표만 필터링
KEY_INDICATORS = {
    "to_in_001": "총인구",
    "to_em_020": "총종사자수",
}

key_df = merged[merged["indicator"].isin(KEY_INDICATORS.keys())].copy()
key_df["indicator_name"] = key_df["indicator"].map(KEY_INDICATORS)

# 집계구별 합산
summary = (
    key_df.groupby(["region", "census_code", "indicator_name"])["value"]
    .sum()
    .reset_index()
)

# 피벗 (집계구 × 지표)
pivot = summary.pivot_table(
    index=["region", "census_code"],
    columns="indicator_name",
    values="value",
    aggfunc="sum"
).reset_index()

pivot.columns.name = None

print("=== 집계구별 인구·종사자 피벗 ===")
print(pivot.head(10).to_string())
print(f"\n총 집계구 수: {len(pivot)}")
print(f"\n=== 지역별 합산 ===")
print(pivot.groupby("region")[["총인구", "총종사자수"]].sum().to_string())

# 저장
pivot.to_csv("data/processed/census_summary.csv", index=False, encoding="utf-8-sig")
print("\n→ data/processed/census_summary.csv 저장 완료!")