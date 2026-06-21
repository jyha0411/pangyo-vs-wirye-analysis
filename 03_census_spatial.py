import geopandas as gpd
import pandas as pd
import json
import os

os.makedirs("data/processed", exist_ok=True)

# 경계 GeoJSON 로드
pangyo_boundary = gpd.read_file("data/processed/boundary_pangyo.geojson").to_crs(epsg=5179)
wirye_boundary = gpd.read_file("data/processed/boundary_wirye.geojson").to_crs(epsg=5179)

# 집계구 shapefile 로드
shp_files = {
    "11240": "data/raw/census_boundary/bnd_oa_11240_2025_2Q.shp",
    "31021": "data/raw/census_boundary/bnd_oa_31021_2025_2Q.shp",
    "31023": "data/raw/census_boundary/bnd_oa_31023_2025_2Q.shp",
    "31180": "data/raw/census_boundary/bnd_oa_31180_2025_2Q.shp",
}

gdfs = []
for code, path in shp_files.items():
    gdf = gpd.read_file(path)
    gdf["sigungu"] = code
    gdfs.append(gdf)

all_oa = pd.concat(gdfs, ignore_index=True)
all_oa = all_oa.to_crs(epsg=5179)

# 구역 내 집계구 필터링
pangyo_oa = gpd.sjoin(all_oa, pangyo_boundary, how="inner", predicate="intersects")[["TOT_OA_CD", "geometry"]].copy()
wirye_oa  = gpd.sjoin(all_oa, wirye_boundary,  how="inner", predicate="intersects")[["TOT_OA_CD", "geometry"]].copy()

pangyo_oa["region"] = "pangyo"
wirye_oa["region"]  = "wirye"

# Census CSV 로드
census_df = pd.read_csv("data/processed/census_summary.csv", encoding="utf-8-sig")
census_df["census_code"] = census_df["census_code"].astype(str)

# 조인
def join_census(oa_gdf, label):
    merged = oa_gdf.merge(
        census_df[["census_code", "총인구", "총종사자수"]],
        left_on="TOT_OA_CD",
        right_on="census_code",
        how="left"
    )
    matched = merged["총인구"].notna().sum()
    print(f"[{label}] 집계구 {len(merged)}개 중 Census 매칭: {matched}개")
    print(f"  총인구 합계: {merged['총인구'].sum():,.0f}")
    print(f"  총종사자수 합계: {merged['총종사자수'].sum():,.0f}")
    return merged

pangyo_census = join_census(pangyo_oa, "판교")
wirye_census  = join_census(wirye_oa,  "위례")

# WGS84로 변환 후 GeoJSON 저장
for gdf, name in [(pangyo_census, "pangyo"), (wirye_census, "wirye")]:
    out = gdf.to_crs(epsg=4326)
    out.to_file(f"data/processed/census_{name}.geojson", driver="GeoJSON")
    print(f"→ data/processed/census_{name}.geojson 저장 완료!")

print("\n=== 최종 비교 ===")
print(f"{'':10} {'총인구':>12} {'총종사자수':>12}")
print(f"{'판교':10} {pangyo_census['총인구'].sum():>12,.0f} {pangyo_census['총종사자수'].sum():>12,.0f}")
print(f"{'위례':10} {wirye_census['총인구'].sum():>12,.0f} {wirye_census['총종사자수'].sum():>12,.0f}")