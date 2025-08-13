# **PRD – 가게 전화 AI 에이전트**

**버전**: v1.2
**작성일**: 2025-08-11

---

## 1. 개요

가게(식당, 미용실 등) 전화를 대신 받아주는 AI 에이전트를 개발한다.
AI는 고객의 문의에 실시간 응대할 수 있도록 **메뉴·시술 서비스, 영업시간, 혼잡도(인기 시간대)** 정보를 자동 수집·정규화·갱신한다.
데이터 수집은 **네이버 지도 URL**로부터 **placeId**를 추출해 **모바일 플레이스 표준 URL**로 변환 후, Firecrawl MCP로 크롤링하여 이뤄진다.
혼잡도 데이터가 없으면 **내부 추론 로직**으로 대체한다.

---

## 2. 목표

* 고객 문의의 90% 이상 자동 처리.
* 메뉴/서비스·영업시간·혼잡도 최신 유지.
* 혼잡도 미제공 시 추론값 안내.
* 점주 요청 시 휴먼 핸드오프.

---

## 3. 범위(Scope)

### 포함 기능

1. **URL 처리**

   * 입력: PC 지도 URL, 모바일 플레이스 URL, placeId, 검색 키워드.
   * placeId 추출 → 업종별 모바일 플레이스 URL 생성.
2. **데이터 수집**

   * 메뉴(식당) / 시술 서비스(미용실)
   * 영업시간(브레이크 타임 포함)
   * 혼잡도(네이버 제공 시) + 미제공 시 추론
   * 전화번호, 주소, 편의시설, 사진
3. **데이터 정규화**

   * MongoDB 스키마 구조화.
   * 요일별 시간 확장, 혼잡도 0\~100 스케일링, 가격/옵션 파싱.
4. **동기화 파이프라인**

   * 초도 수집 → 정규화 → 저장.
   * 변경 감지 → 점주 알림.
5. **AI 에이전트**

   * 영업시간·예약 가능·가격 안내.
   * 혼잡도 기반 방문 추천.
   * 휴먼 핸드오프.

---

## 4. URL 표준화 로직

### 4.1 placeId 추출

* 예:
  `https://map.naver.com/p/entry/place/1690334952?...`
  → `/entry/place/(\d+)` 정규식으로 placeId 추출 → `1690334952`

### 4.2 모바일 플레이스 URL 생성

* 업종 카테고리(식당 기본):

  * home: `https://m.place.naver.com/restaurant/{placeId}/home`
  * menu: `https://m.place.naver.com/restaurant/{placeId}/menu`
  * info: `https://m.place.naver.com/restaurant/{placeId}/info`

### 4.3 예시

* 입력:
  `https://map.naver.com/p/entry/place/1690334952?...`
* 표준화:

  * home: `https://m.place.naver.com/restaurant/1690334952/home`
  * menu: `https://m.place.naver.com/restaurant/1690334952/menu`
  * info: `https://m.place.naver.com/restaurant/1690334952/info`

---

## 5. 데이터 모델 (MongoDB)

```json
{
  "_id": "place_1690334952",
  "source": {
    "platform": "naver",
    "placeId": "1690334952",
    "lastFetchedAt": "2025-08-11T04:20:00Z",
    "sourceUrl": "https://m.place.naver.com/restaurant/1690334952/home"
  },
  "profile": {
    "name": "가게명",
    "phone": "02-123-4567",
    "category": ["음식점", "피자"],
    "address": { "road": "...", "lot": "...", "coords": { "lat": 0, "lng": 0 } }
  },
  "hours": [
    { "day": "MON", "open": "11:00", "close": "21:30", "break": [{"start":"15:00","end":"17:00"}], "lastOrder": "21:00" }
  ],
  "popularTimes": {
    "now": { "label": null, "score": null, "source": "absent", "confidence": 0.0 },
    "hourly": [],
    "sources": { "naver_text": false, "inference": false },
    "lastComputedAt": null
  },
  "restaurant": { "menu": [] },
  "salon": { "services": [] },
  "amenities": [],
  "images": [],
  "agentOverrides": {}
}
```

---

## 6. Firecrawl MCP 요청 예시

### 메뉴

```json
{
  "url": "https://m.place.naver.com/restaurant/1690334952/menu",
  "render_js": false,
  "extract": {
    "type": "json",
    "selectors": [
      {
        "name": "menuItems",
        "selector": "div[class*='menu_list'] li, ul[class*='menu_list'] li",
        "fields": {
          "name": ".title, .menu_name",
          "price": ".price, .amount",
          "desc": ".desc, .menu_desc"
        }
      }
    ]
  }
}
```

### 영업시간

```json
{
  "url": "https://m.place.naver.com/restaurant/1690334952/info",
  "render_js": false,
  "extract": {
    "type": "json",
    "selectors": [
      {
        "name": "hours",
        "selector": "[class*='business_hours'] li, [class*='operation'] li",
        "fields": { "day": ".day", "time": ".time" }
      }
    ]
  }
}
```

### 혼잡도(텍스트 전체, 파싱은 백엔드)

```json
{
  "url": "https://m.place.naver.com/restaurant/1690334952/home",
  "render_js": false,
  "extract": { "type": "markdown" },
  "timeout": 20000
}
```

---

## 7. 혼잡도 추출/추론 로직

### 7.1 네이버 제공 시

* `markdown` 텍스트에서 “혼잡/여유/보통/붐빔” 키워드 또는 `__APOLLO_STATE__` 등 초기 상태 JSON 파싱.
* 라벨 → 0\~100 점수 매핑:

  * 여유: 25 / 보통: 50 / 혼잡: 80 / 붐빔: 90

### 7.2 미제공 시

* 업종별 기본 패턴(priors):

  * 음식점: 점심(12–13시), 저녁(18–20시) 피크
  * 미용실: 주말 오전\~오후 피크
* 내부 신호 보정:

  * 최근 통화량, 예약 슬롯 점유율, 대기시간
* 결합:

  * `score = 0.6*prior + 0.4*signal`
  * confidence 낮으면 “정확하지 않을 수 있음” 안내

---

## 8. 파이프라인 플로우

1. **입력 처리**

   * URL/ID → placeId → 모바일 URL 생성
2. **탭별 크롤링**

   * 메뉴 / 정보 / 홈(markdown)
3. **정규화**

   * 시간/가격/혼잡도 변환
4. **혼잡도 처리**

   * 제공 시 → 파싱
   * 미제공 시 → 추론
5. **DB 업데이트**

   * 변경 필드만 업데이트
6. **알림**

   * 변경 사항 점주 통지
7. **스케줄링**

   * hours: 주 1회, menu/services: 월 1~~2회, popularTimes: 1~~3일 간격

---

## 9. AI 응답 정책

* **네이버 혼잡도 있음**:
  “지금은 보통(50/100)입니다. 19시 이후 혼잡할 수 있어요.”
* **미제공 + 추론값**:
  “네이버 혼잡도는 없지만, 내부 추정으로 현재 보통(48/100)입니다.”
* **confidence<0.5**:
  “정확하지 않을 수 있어요. 대기 여부 확인해드릴까요?”

---

## 10. 비기능 요건

* 수집 속도 ≤ 5초/페이지
* 필드별 수집 주기 조절
* 변경 감지 정확도 ≥ 95%
* API 키/크롤러 IP 보안
