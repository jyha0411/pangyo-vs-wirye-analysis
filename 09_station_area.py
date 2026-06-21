import geopandas as gpd
import pandas as pd
import json
import os
from shapely.geometry import Point

os.makedirs("data/processed", exist_ok=True)

# 지하철역 로드
nodes = pd.read_csv("data/raw/subway_network/network/nodes.tsv", sep="\t")

# 경계 로드
pangyo_boundary = gpd.read_file("data/processed/boundary_pangyo.geojson").to_crs(epsg=5179)
wirye_boundary  = gpd.read_file("data/processed/boundary_wirye.geojson").to_crs(epsg=5179)

# 역 GeoDataFrame 생성
stations_gdf = gpd.GeoDataFrame(
    nodes,
    geometry=gpd.points_from_xy(nodes["lng"], nodes["lat"]),
    crs="EPSG:4326"
).to_crs(epsg=5179)

# 역세권 500m / 1km 버퍼
for radius, label in [(500, "500m"), (1000, "1km")]:
    buffers = stations_gdf.copy()
    buffers["geometry"] = buffers.geometry.buffer(radius)
    buffers_union = buffers.unary_union

    for region, boundary, name in [
        ("pangyo", pangyo_boundary, "판교"),
        ("wirye",  wirye_boundary,  "위례"),
    ]:
        region_area  = boundary.geometry.iloc[0].area
        overlap      = boundary.geometry.iloc[0].intersection(buffers_union).area
        ratio        = round(overlap / region_area * 100, 1)
        print(f"[{name}] 역세권 {label} 커버리지: {ratio}% (구역면적 {region_area/1e6:.2f}㎢)")

# 구역 내 역 수
for region, boundary, name in [
    ("pangyo", pangyo_boundary, "판교"),
    ("wirye",  wirye_boundary,  "위례"),
]:
    within = gpd.sjoin(stations_gdf, boundary, how="inner", predicate="within")
    unique = within["statnm"].nunique()
    print(f"[{name}] 구역 내 역 수: {unique}개")