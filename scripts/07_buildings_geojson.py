import pandas as pd
import geopandas as gpd
import json
import os

os.makedirs("data/processed", exist_ok=True)

USE_COLOR = {
    "office": "#fd79a8", "commercial": "#e17055", "retail": "#e17055",
    "residential": "#4a9eff", "apartments": "#4a9eff", "house": "#74b9ff",
    "school": "#fdcb6e", "university": "#fdcb6e", "hospital": "#6c5ce7",
    "industrial": "#b2bec3", "warehouse": "#b2bec3", "yes": "#636e72",
}
USE_KO = {
    "office":"업무시설","commercial":"판매·상업시설","retail":"판매시설",
    "residential":"공동주택","apartments":"공동주택","house":"단독주택",
    "school":"교육연구시설","university":"교육연구시설","hospital":"의료시설",
    "industrial":"공업시설","warehouse":"창고시설","yes":"건물",
    "church":"종교시설","kindergarten":"교육연구시설","civic":"공공시설",
}
def bld_color(use):
    # USE_KO 변환 후 한국어 용도로도 색상 매핑
    KO_COLOR = {
        "업무시설": "#fd79a8", "판매·상업시설": "#e17055", "판매시설": "#e17055",
        "공동주택": "#4a9eff", "단독주택": "#74b9ff",
        "교육연구시설": "#fdcb6e", "의료시설": "#6c5ce7",
        "공업시설": "#b2bec3", "창고시설": "#b2bec3",
        "공공시설": "#55efc4", "종교시설": "#fab1a0",
    }
    return USE_COLOR.get(use) or KO_COLOR.get(USE_KO.get(use, ""), "#636e72")

# 판교 건축물대장 로드
print("판교 건축물대장 로드 중...")
df_bd = pd.read_csv(
    "data/raw/buildings/건축물대장_jyha_20260620223946분당.csv",
    encoding="utf-8", low_memory=False
)
pangyo_dongs = ["백현동", "삼평동", "판교동", "하산운동"]
df_bd = df_bd[df_bd["법정동"].isin(pangyo_dongs)].copy()
df_bd["건물명"] = df_bd["건물명"].fillna("")
print(f"판교 건축물대장: {len(df_bd)}건")

# OSM에서 판교 건물 추출
print("OSM geopackage에서 판교 건물 추출 중...")
boundary = gpd.read_file("data/processed/boundary_pangyo.geojson")
gdf = gpd.read_file(
    "data/raw/osm/planet_127.0625,37.3805_127.1795,37.4494-geopackage/planet_127.0625,37.3805_127.1795,37.4494.gpkg",
    layer="multipolygons"
)
buildings = gdf[gdf["building"].notna()].copy()
buildings = buildings.to_crs(epsg=4326)
boundary  = boundary.to_crs(epsg=4326)
pangyo_buildings = gpd.clip(buildings, boundary)
print(f"판교 내 건물 수: {len(pangyo_buildings)}")

# 건축물대장에서 건물명으로 매칭
name_to_row = {}
for _, row in df_bd.iterrows():
    nm = str(row["건물명"]).strip()
    if nm and nm not in name_to_row:
        name_to_row[nm] = row

pangyo_out = []
matched_count = 0
for _, row in pangyo_buildings.iterrows():
    use     = str(row.get("building", ""))
    use_ko  = USE_KO.get(use, use)
    bldg_name = str(row.get("name", ""))
    if bldg_name == "nan": bldg_name = ""
    dong = ""

    연면적 = 0; 층수 = 0; 용적률 = 0

    # 건물명으로 매칭
    best = None
    if bldg_name:
        for nm, r in name_to_row.items():
            if nm and (nm in bldg_name or bldg_name in nm):
                best = r
                break

    if best is not None:
        matched_count += 1
        연면적  = round(float(best["연면적(㎡)"]), 1)  if pd.notna(best.get("연면적(㎡)"))  else 0
        층수    = int(best["지상층수"])                 if pd.notna(best.get("지상층수"))    else 0
        용적률  = round(float(best["용적률(%)"]), 1)   if pd.notna(best.get("용적률(%)"))   else 0
        dong   = str(best.get("법정동", ""))
        if pd.notna(best.get("주용도")):
            use_ko = str(best["주용도"])
    else:
        # 매칭 안 된 경우 중심점 좌표로 동 추정
        try:
            cx = row["geometry"].centroid.x
            cy = row["geometry"].centroid.y
            if cx >= 127.108 and cy >= 37.394:
                dong = "백현동"
            elif cx >= 127.100:
                dong = "삼평동"
            else:
                dong = "판교동"
        except:
            dong = "판교동"
    pangyo_out.append({
        "type": "Feature",
        "properties": {
            "주용도":   use_ko,
            "건물명":   bldg_name,
            "법정동":   dong,
            "연면적":   연면적,
            "지상층수": 층수,
            "용적률":   용적률,
            "color":    bld_color(use),
            "region":   "pangyo"
        },
        "geometry": row["geometry"].__geo_interface__
    })

print(f"건축물대장 매칭: {matched_count}/{len(pangyo_out)}개")
pangyo_geojson = {"type": "FeatureCollection", "features": pangyo_out}
with open("data/processed/buildings_pangyo.geojson", "w", encoding="utf-8") as f:
    json.dump(pangyo_geojson, f, ensure_ascii=False)
print(f"→ buildings_pangyo.geojson 저장 완료! ({len(pangyo_out)}개)")