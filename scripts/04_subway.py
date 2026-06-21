import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import dijkstra
import json
import os

os.makedirs("data/processed", exist_ok=True)

nodes = pd.read_csv("data/raw/subway_network/network/nodes.tsv", sep="\t")
links = pd.read_csv("data/raw/subway_network/network/links.tsv", sep="\t")

print(f"노드 수: {len(nodes)}, 링크 수: {len(links)}")

# 그래프 생성
V = len(nodes)
u = links["fromNode"].to_numpy()
v = links["toNode"].to_numpy()
src = np.concatenate([u, v])
dst = np.concatenate([v, u])
cost = np.concatenate([links["timeFT"].to_numpy(), links["timeTF"].to_numpy()]).astype(np.float32)
A = csr_matrix((cost, (src, dst)), shape=(V, V))

# 출발역 설정 (환승역은 두 노드 중 작은 비용으로 합산)
origins = {
    "판교": [26, 824],    # 경강선 + 신분당선
    "남위례": [239, 735], # 위례선 + 서울8호선
}

results = {}
THRESHOLD = 30 * 60  # 30분 = 1800초

for name, ids in origins.items():
    # 두 노드에서 각각 Dijkstra 후 최솟값 사용
    dist_all = []
    for sid in ids:
        d = dijkstra(A, indices=sid, directed=True)
        dist_all.append(d)
    dist = np.min(dist_all, axis=0)

    # 30분 이내 도달 가능한 역
    reachable = nodes[dist <= THRESHOLD].copy()
    reachable["travel_sec"] = dist[reachable["id"].values]
    reachable["travel_min"] = (reachable["travel_sec"] / 60).round(1)

    print(f"\n=== {name}역 30분 등시간권 ===")
    print(f"도달 가능 노드 수: {len(reachable)}")
    print(f"도달 가능 역 수 (중복 제거): {reachable['statnm'].nunique()}")
    print(reachable[["statnm", "linenm", "travel_min"]].sort_values("travel_min").head(20).to_string())

    results[name] = reachable

    # GeoJSON 저장
    features = []
    for _, row in reachable.iterrows():
        features.append({
            "type": "Feature",
            "properties": {
                "statnm": row["statnm"],
                "linenm": row["linenm"],
                "travel_min": row["travel_min"],
                "origin": name
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row["lng"], row["lat"]]
            }
        })

    geojson = {"type": "FeatureCollection", "features": features}
    out_path = f"data/processed/isochrone_{name}.geojson"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    print(f"→ {out_path} 저장 완료!")

# 비교 요약
print("\n=== 최종 비교 ===")
for name, df in results.items():
    print(f"{name}역: {df['statnm'].nunique()}개 역 30분 내 도달 가능")