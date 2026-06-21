import geopandas as gpd
import pandas as pd
import numpy as np
import alphashape
import json
import os
from shapely.geometry import mapping

os.makedirs("data/processed", exist_ok=True)

nodes = pd.read_csv("data/raw/subway_network/network/nodes.tsv", sep="\t")
links = pd.read_csv("data/raw/subway_network/network/links.tsv", sep="\t")

from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra

V = len(nodes)
u = links["fromNode"].to_numpy()
v = links["toNode"].to_numpy()
src = np.concatenate([u, v])
dst = np.concatenate([v, u])
cost = np.concatenate([links["timeFT"].to_numpy(), links["timeTF"].to_numpy()]).astype(np.float32)
A = csr_matrix((cost, (src, dst)), shape=(V, V))

origins = {
    "판교": [26, 824],
    "남위례": [239, 735],
}

THRESHOLDS = [30, 60]  # 분

all_features = []

for name, ids in origins.items():
    dist_all = []
    for sid in ids:
        d = dijkstra(A, indices=sid, directed=True)
        dist_all.append(d)
    dist = np.min(dist_all, axis=0)

    for thresh in THRESHOLDS:
        mask = dist <= thresh * 60
        reachable = nodes[mask].copy()
        reachable["travel_min"] = dist[reachable["id"].values] / 60

        pts = list(zip(reachable["lng"], reachable["lat"]))

        if len(pts) < 4:
            continue

        # alphashape으로 폴리곤 생성
        alpha = 0.5
        shape = alphashape.alphashape(pts, alpha)

        if shape is None or shape.is_empty:
            continue

        feature = {
            "type": "Feature",
            "properties": {
                "origin": name,
                "threshold_min": thresh,
                "station_count": int(reachable["statnm"].nunique()),
            },
            "geometry": mapping(shape)
        }
        all_features.append(feature)
        print(f"[{name}] {thresh}분 폴리곤 생성 완료 — 역 {reachable['statnm'].nunique()}개")

geojson = {"type": "FeatureCollection", "features": all_features}
out = "data/processed/isochrone_polygons.geojson"
with open(out, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

print(f"\n→ {out} 저장 완료!")