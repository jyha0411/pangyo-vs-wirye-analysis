import pandas as pd
import geopandas as gpd
import json
import numpy as np
import os
from shapely.geometry import Point

os.makedirs("data/processed", exist_ok=True)

# 경계 로드
pangyo_boundary = gpd.read_file("data/processed/boundary_pangyo.geojson")
wirye_boundary  = gpd.read_file("data/processed/boundary_wirye.geojson")
pangyo_shape = pangyo_boundary.geometry.iloc[0]
wirye_shape  = wirye_boundary.geometry.iloc[0]

USE_COLOR = {
    "공동주택": "#4a9eff", "단독주택": "#74b9ff",
    "제1종근린생활시설": "#55efc4", "제2종근린생활시설": "#00cec9",
    "업무시설": "#fd79a8", "판매시설": "#e17055",
    "교육연구시설": "#fdcb6e", "의료시설": "#6c5ce7",
    "노유자시설": "#a29bfe", "종교시설": "#fab1a0",
}
def get_color(use):
    if not isinstance(use, str): return "#636e72"
    for key, color in USE_COLOR.items():
        if key in use: return color
    return "#636e72"

def random_points_in_polygon(polygon, n, seed=42):
    np.random.seed(seed)
    minx, miny, maxx, maxy = polygon.bounds
    points = []
    attempts = 0
    while len(points) < n and attempts < n * 20:
        batch = np.random.uniform([minx, miny], [maxx, maxy], (min(n*3, 10000), 2))
        for p in batch:
            if polygon.contains(Point(p[0], p[1])):
                points.append((p[0], p[1]))
            if len(points) >= n:
                break
        attempts += len(batch)
    return points[:n]

def make_geojson(df, polygon, region, label):
    df = df[df["주용도"].notna()].reset_index(drop=True)
    print(f"[{label}] {len(df)}건 처리 중...")
    pts = random_points_in_polygon(polygon, len(df))
    
    features = []
    for i, (_, row) in enumerate(df.iterrows()):
        use = str(row.get("주용도", "기타"))
        features.append({
            "type": "Feature",
            "properties": {
                "주용도":   use,
                "연면적":   round(float(row["연면적(㎡)"]), 1) if pd.notna(row.get("연면적(㎡)")) else 0,
                "지상층수": int(row["지상층수"]) if pd.notna(row.get("지상층수")) else 0,
                "용적률":   round(float(row["용적률(%)"]), 1) if pd.notna(row.get("용적률(%)")) else 0,
                "법정동":   str(row.get("법정동", "")),
                "건물명":   str(row.get("건물명", "")),
                "color":    get_color(use),
                "region":   region
            },
            "geometry": {"type": "Point", "coordinates": [pts[i][0], pts[i][1]]}
        })
    print(f"  완료! 용도 분포: {df['주용도'].value_counts().head(5).to_dict()}")
    return features

# ── 위례 ──────────────────────────────────────
wirye_files = [
    ("data/raw/buildings/건축물대장_jyha_20260618014629송파.csv", ["거여동", "장지동"]),
    ("data/raw/buildings/건축물대장_jyha_20260620223905수정.csv", ["창곡동"]),
    ("data/raw/buildings/건축물대장_jyha_20260620223327하남.csv", ["학암동"]),
]

wirye_rows = []
for fpath, dongs in wirye_files:
    df = pd.read_csv(fpath, encoding="utf-8", low_memory=False)
    filtered = df[df["법정동"].isin(dongs)]
    wirye_rows.append(filtered)
    print(f"{dongs}: {len(filtered)}건")

wirye_df = pd.concat(wirye_rows, ignore_index=True)
wirye_features = make_geojson(wirye_df, wirye_shape, "wirye", "위례 전체")

wirye_geojson = {"type": "FeatureCollection", "features": wirye_features}
with open("data/processed/buildings_wirye.geojson", "w", encoding="utf-8") as f:
    json.dump(wirye_geojson, f, ensure_ascii=False)
print(f"→ buildings_wirye.geojson 저장 완료! ({len(wirye_features)}개)\n")

# ── 판교 (분당구 백현동·삼평동·판교동) ──────────
pangyo_dongs = ["백현동", "삼평동", "판교동", "하산운동"]
df_bd = pd.read_csv(
    "data/raw/buildings/건축물대장_jyha_20260620223946분당.csv",
    encoding="utf-8", low_memory=False
)
pangyo_df = df_bd[df_bd["법정동"].isin(pangyo_dongs)]
print(f"판교 관련 동: {pangyo_df['법정동'].value_counts().to_dict()}")

pangyo_bld_features = make_geojson(pangyo_df, pangyo_shape, "pangyo", "판교 건축물대장")

# 판교는 OSM만 사용 (이미 buildings_pangyo.geojson 있음)
print(f"→ 판교는 OSM 데이터 유지 (683개 폴리곤)")