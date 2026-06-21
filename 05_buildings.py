import pandas as pd
import os

os.makedirs("data/processed", exist_ok=True)

# 송파 건축물대장 전체 로드
print("송파 건축물대장 로드 중...")
df = pd.read_csv(
    "data/raw/buildings/건축물대장_jyha_20260618014629송파.csv",
    encoding="utf-8"
)

print(f"전체 행 수: {len(df)}")

# 위례신도시 법정동 필터링
# 위례신도시 = 송파구 장지동, 거여동, 오금동, 방이동 일부
wirye_dongs = ["거여동", "장지동"]
df_wirye = df[df["법정동"].isin(wirye_dongs)].copy()
print(f"위례 관련 법정동 건물 수: {len(df_wirye)}")
print(f"포함 법정동: {df_wirye['법정동'].unique().tolist()}")

# 전체 송파 용도 분포
print("\n=== 송파 전체 주용도 분포 (상위 15) ===")
print(df["주용도"].value_counts().head(15).to_string())

# 위례 용도 분포
print("\n=== 위례 법정동 주용도 분포 ===")
if len(df_wirye) > 0:
    print(df_wirye["주용도"].value_counts().to_string())
else:
    print("해당 법정동 데이터 없음")
    print("\n전체 법정동 목록:")
    print(df["법정동"].value_counts().head(20).to_string())