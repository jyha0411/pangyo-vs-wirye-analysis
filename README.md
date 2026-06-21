# 데이터로 진단하는 업무지구의 성공과 실패 — 판교테크노밸리 비교분석 시스템 구축

## 프로젝트 개요
판교테크노밸리(성공 사례)와 위례신도시(활성화 저조 업무단지)를 대상으로
토지이용, 교통망, 인구사회 지표를 비교분석한 웹 기반 시각화 시스템

## 배포 URL
https://jyha0411.github.io/pangyo-vs-wirye-analysis/docs/index.html

## 데이터 출처 및 기준 시점
- **건축물 용도 (판교)**: OpenStreetMap (OSM) 건물 폴리곤 + 건축HUB 건축물대장 — 성남시 분당구 (2026년 6월 기준)
- **건축물 용도 (위례)**: 건축HUB 건축물대장 — 송파구·성남시 수정구·하남시 (2026년 6월 기준)
- **집계구 단위 인구 및 종사자 수**: SGIS 통계지리정보서비스 (2023~2024년 기준)
- **집계구 경계 Shapefile**: SGIS 통계지리정보서비스 — 송파구·분당구·수정구·하남시 (2025년 2분기 기준)
- **도로망 및 건물 폴리곤**: OpenStreetMap (OSM) Geopackage (2026년 6월 기준)
- **수도권 지하철 네트워크**: 자료 제공 (LMS 배포) `subway_network.zip` 

## 데이터 처리 및 분석 과정

본 프로젝트는 데이터의 재현성을 위해 전처리부터 분석까지 단계별 파이썬 스크립트로 모듈화하여 수행하였음.

1. **구역 경계 설정** (`01_boundary.py`)  
   분석 대상지(판교테크노밸리, 위례신도시)의 공간적 범위 설정 및 GeoJSON 폴리곤 생성

2. **인구사회 데이터 전처리** (`02_census.py`, `03_census_spatial.py`)  
   SGIS 집계구 데이터를 분석 구역 경계와 공간 결합하여 인구·종사자수 매핑 및 직주비 산출

3. **교통망 및 등시간권 분석** (`04_subway.py`, `06_isochrone_polygon.py`, `09_station_area.py`)  
   `subway_network.zip` 기반 Dijkstra 최단경로 알고리즘으로 30분/60분 등시간권 폴리곤 생성 및 역세권 면적 비율(500m/1km) 산출

4. **토지이용 및 건축물 데이터 가공** (`05_buildings.py`, `07_buildings_geojson.py`, `08_geocoding.py`)  
   OSM 건물 폴리곤과 건축물대장을 결합하여 용도별 GeoJSON 생성.  
   위례 건축물은 좌표 미제공으로 구역 경계 내 격자 배치 방식 적용 (한계점으로 명시)

## 실행 방법

### 1. 필수 라이브러리 설치
```bash
pip install geopandas pandas shapely pyproj alphashape scipy
```

### 2. 데이터 전처리 및 공간 분석 순차 실행
```bash
python scripts/01_boundary.py
python scripts/02_census.py
python scripts/03_census_spatial.py
python scripts/04_subway.py
python scripts/05_buildings.py
python scripts/06_isochrone_polygon.py
python scripts/07_buildings_geojson.py
python scripts/08_geocoding.py
python scripts/09_station_area.py
```

### 3. 로컬 웹 서버 구동
```bash
python -m http.server 8000
```
브라우저에서 접속: `http://localhost:8000/docs/index.html`

## 주요 분석 결과
| 지표 | 판교 | 위례 |
|------|------|------|
| 총인구 | 31,107명 | 108,020명 |
| 총종사자수 | 100,022명 | 33,880명 |
| 직주비 (종사자/인구) | **3.22** | 0.31 |
| 30분 도달 역 수 | 85개 | 90개 |
| 역세권 500m 커버리지 | 19.8% | 58.8% |
| 역세권 1km 커버리지 | 59.6% | 96.3% |
| 업무시설 비율 | **11.8%** | 0.9% |
