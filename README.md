# 판교테크노밸리 vs 위례신도시 스마트 업무단지 비교분석

## 프로젝트 개요
판교테크노밸리(성공 사례)와 위례신도시(미성숙 업무단지)를 대상으로 토지이용, 교통망, 인구사회 지표를 비교분석한 웹 기반 시각화 시스템

## 배포 URL
[https://jyha0411.github.io/pangyo-vs-wirye-analysis/docs/](https://jyha0411.github.io/pangyo-vs-wirye-analysis/docs/)

## 데이터 출처
- 건축물대장: 국토교통부 건축데이터민간개방시스템
- 집계구 경계: SGIS 통계지리정보서비스
- 지하철 네트워크: 수도권 지하철 네트워크 데이터셋 (2026)
- OSM: OpenStreetMap (판교 건물 폴리곤)
- 토지이용계획: 국토정보플랫폼

## 분석 내용
- 3-1. 토지이용: 건물 용도 분포 비교 (OSM + 건축물대장)
- 3-2. 교통망: 지하철 30/60분 등시간권, 역세권 면적 비율
- 3-3. 인구사회: 인구·종사자·직주비 비교

## 실행 방법

1. 필수 라이브러리 설치
pip install geopandas pandas shapely pyproj alphashape scipy

2. 데이터 전처리 및 공간 분석 파이썬 스크립트 실행
python scripts/01_boundary.py
python scripts/02_census.py
python scripts/03_census_spatial.py
python scripts/04_subway.py
python scripts/06_isochrone_polygon.py
python scripts/07_buildings_geojson.py
python scripts/08_geocoding.py
python scripts/09_station_area.py

3. 로컬 웹 서버 구동 및 시스템 확인
python -m http.server 8000

서버가 실행되면 웹 브라우저를 열고 아래 주소로 접속합니다:
http://localhost:8000/docs/index.html
