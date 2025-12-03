# 소프트웨어 파트 정리

(라즈베리파이 + Flask + ADC + GPIO 기반)

**센서 입력 → Flask 서버 처리 → 라즈베리파이 제어 → Web UI 표시**

## **1. 전체 소프트웨어 구조**

```
smart_pot/
│  app.py               → Flask 메인 서버
│  sensor.py            → 센서 및 펌프, LED 제어
│
├─ templates/
│   ├ home.html         → 메인 화면(식물 이미지/물주기)
│   └ status.html       → 상태 화면(센서값/그래프)
│
└─ static/
    ├ img/              → UI 이미지(식물, 팝업, 버튼)
    └ style.css         → 전체 디자인

```

**동작흐름**

```
센서값 읽기 (PCF8591)
        ↓
Flask API 제공 (/api/sensor)
        ↓
프론트엔드 JS가 5초마다 fetch
        ↓
UI 업데이트 (식물 표정 변경, 그래프 변경)
        ↓
조도/수분 조건 검사 → 자동 팝업
        ↓
조도 부족 시 → LED ON
        ↓
사용자가 물주기 클릭 → /api/water → 펌프 작동

```

---

## **2. 센서 및 제어 로직(sensor.py)**

### **핵심 기능**

- PCF8591 (I2C ADC)에서 **광(A0), 수분(A2)** 데이터 읽기
- 센서 raw 값(0~255)를 퍼센트로 변환
    - 수분: 역퍼센트 변환 (255-raw)/255*100 → 마를수록 값↓
    - 조도: raw/255*100 → 어두울수록 값 ↓
- 조도값 기준으로 LED 자동 제어
    - light < 30 → LED ON
- /api/water 요청 시 워터펌프 동작
    
    

### **코드 요약**

```python
def read_moisture():
    raw = read_adc(2)          # A2
    return round((255 - raw) / 255 * 100, 1)

def read_light():
    raw = read_adc(0)          # A0
    return round(raw / 255 * 100, 1)

def get_sensor_data():
    moisture = read_moisture()
    light = read_light()

    if light < 30:
        GPIO.output(LED_PIN, GPIO.HIGH)
    else:
        GPIO.output(LED_PIN, GPIO.LOW)

    return {"moisture": moisture, "light": light}

```

---

## **3. Flask 서버 + API(app.py)**

### **API 목록**

| API | 설명 |
| --- | --- |
| `/api/sensor` | 광/수분 센서값을 JSON으로 반환 |
| `/api/water` | 워터펌프 2초 동작 |
| `/home` | 메인 UI |
| `/status` | 상태 페이지 |

### 코드 요약

```python
@app.route("/api/sensor")
def api_sensor():
    data = get_sensor_data()
    return jsonify(data)

@app.route("/api/water")
def api_water():
    pump_on()
    time.sleep(2)
    pump_off()
    return jsonify({"success": True})
```

---

## **4. 앱 UI**

5초마다 /api/sensor를 호출하여 실시간으로 UI를 자동 업데이트

**① 실시간 데이터 요청 (5초 간격)**

**② UI 업데이트**

**③ 자동 알림 및 펌프 제어 호출**

---

### 4-1. 홈 화면 UI (home.html)

**홈 화면 주요 기능** 

**1) 실시간 센서 기반 UI 변경**

- 5초 주기로 조도·수분 값 갱신
- 값에 따라 식물 표정 4종 자동 변경
    
    (건강 / 말라감 / 어두움 / 슬픔)
    
- 조도가 낮으면 화면에 `dark-overlay` 적용

**2) 물주기 기능**

- “물 주기” 버튼 클릭 시
    
    → `/api/water` 호출
    
    → 워터펌프 동작
    

**3) 팝업 알림 시스템 (홈 화면 내에서 동작)**

- 센서 상태가 기준값 이하일 때 팝업 이미지 자동 표시
- 1분 쿨다운 적용 → 연속 알림 방지
- 조건:
    - `moisture < 30` → 수분 부족 팝업
    - `light < 30` → 빛 부족 팝업
- 팝업 클릭 시 사라짐

```jsx
function maybeShowAlerts(light, moisture) {
  if (moisture < 30) showPopup("/static/img/popup_moisture.png");
  if (light < 30) showPopup("/static/img/popup_light.png");
}
```

### 4-2. 상태 화면 UI (status.html)

**상태 화면 주요 기능: 데이터 시각화 중심** 

- 실시간 조도·수분 퍼센트 표시
- 수평 막대 그래프(width %로 표현)
- 시각적으로 상태를 모니터링
