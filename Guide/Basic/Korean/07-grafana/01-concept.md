# 07 설명 — Grafana가 데이터를 보여주는 방법

Grafana는 여러 저장 도구의 데이터를 한 화면에서 보여줍니다. Grafana 자체가 Mimir·Loki·Tempo 대신 모든 관측 데이터를 저장하는 것은 아닙니다. 직접 만든 Dashboard와 사용자 설정은 Grafana의 PVC에 저장합니다.

**데이터 소스(Data source)**는 Grafana가 데이터를 읽을 곳입니다. 이 실습에서는 Mimir·Loki·Tempo 세 개를 미리 연결합니다. **쿼리(Query)**는 그곳에 어떤 데이터를 달라고 요청하는 문장입니다.

**Explore**는 데이터를 먼저 찾아보는 화면입니다. **Dashboard**는 자주 볼 내용을 모아 저장하는 화면입니다. Dashboard의 작은 상자 하나를 **패널(Panel)**이라고 부릅니다.

이번에는 Explore에서 메트릭과 로그가 실제로 들어오는지 확인합니다. 이 확인을 먼저 하면 Dashboard에서 데이터가 없을 때 수집 문제인지 그래프 설정 문제인지 구분하기 쉽습니다. 트레이스는 서버 자동 계측 이후 확인합니다.

[목차](../README.md) · [이어서 실습하기](02-practice.md)
