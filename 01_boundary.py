import json
import os

os.makedirs("data/processed", exist_ok=True)

# 판교 제1+2 테크노밸리 경계 (근사 폴리곤, WGS84)
pangyo = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "판교테크노밸리", "region": "pangyo"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [127.0940, 37.3990],
                [127.1150, 37.3990],
                [127.1150, 37.3870],
                [127.0940, 37.3870],
                [127.0940, 37.3990]
            ]]
        }
    }]
}

# 위례신도시 업무·상업용지 경계 (근사 폴리곤, WGS84)
wirye = {
    "type": "FeatureCollection",
    "features": [{
        "type": "Feature",
        "properties": {"name": "위례신도시", "region": "wirye"},
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [127.1480, 37.4720],
                [127.1700, 37.4720],
                [127.1700, 37.4560],
                [127.1480, 37.4560],
                [127.1480, 37.4720]
            ]]
        }
    }]
}

with open("data/processed/boundary_pangyo.geojson", "w", encoding="utf-8") as f:
    json.dump(pangyo, f, ensure_ascii=False, indent=2)

with open("data/processed/boundary_wirye.geojson", "w", encoding="utf-8") as f:
    json.dump(wirye, f, ensure_ascii=False, indent=2)

print("경계 GeoJSON 생성 완료!")
print("  → data/processed/boundary_pangyo.geojson")
print("  → data/processed/boundary_wirye.geojson")
print("\n⚠️  geojson.io 에서 경계 확인 후 수정 필요!")