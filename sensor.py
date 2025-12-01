import smbus2 as smbus
import RPi.GPIO as GPIO
import time

# -----------------------------
# PCF8591 설정
# -----------------------------
I2C_BUS = 1
PCF_ADDR = 0x48
bus = smbus.SMBus(I2C_BUS)

def read_adc(channel):
    """
    PCF8591 ADC 읽기
    channel: 0~3
    """
    if channel < 0 or channel > 3:
        return 0
    
    bus.write_byte(PCF_ADDR, 0x40 | channel)
    bus.read_byte(PCF_ADDR)  # dummy read
    adc_value = bus.read_byte(PCF_ADDR)
    return adc_value


# -----------------------------
# 수분 센서 읽기 (AIN2)
# -----------------------------
def read_moisture():
    raw = read_adc(2)  # A2
    moisture = (255-raw) / 255.0 * 100.0
    print(f"[DEBUG] raw_moisture={raw}, moisture={moisture:.1f}%")
    return round(moisture, 1)


# -----------------------------
# 조도 센서 읽기 (AIN0)
# -----------------------------
def read_light():
    raw = read_adc(0)  # A0
    light = (255 - raw) / 255.0 * 100.0
    print(f"[DEBUG] raw_light={raw}, light={light:.1f}%")
    return round(light, 1)



# -----------------------------
# 워터펌프 설정
# -----------------------------
PUMP_PIN = 17   # MOSFET 제어 (BCM17)
LED_PIN = 18    # 선택사항: LED 표시용

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(PUMP_PIN, GPIO.OUT)
GPIO.setup(LED_PIN, GPIO.OUT)

GPIO.output(PUMP_PIN, GPIO.LOW)
GPIO.output(LED_PIN, GPIO.LOW)


# -----------------------------
# 펌프 제어 함수
# -----------------------------
def pump_on():
    print("펌프 ON")
    GPIO.output(PUMP_PIN, GPIO.HIGH)
    GPIO.output(LED_PIN, GPIO.HIGH)

def pump_off():
    print("펌프 OFF")
    GPIO.output(PUMP_PIN, GPIO.LOW)
    GPIO.output(LED_PIN, GPIO.LOW)


# -----------------------------
# 센서 종합 함수
# -----------------------------
def get_sensor_data():
    try:
        moisture = read_moisture()
        light = read_light()

        # -----------------------------
        # 자동 LED 제어
        # -----------------------------
        LIGHT_THRESHOLD = 30   # 어두워지는 기준 (원하면 조정 가능)

        if light < LIGHT_THRESHOLD:
            GPIO.output(LED_PIN, GPIO.HIGH)   # LED 켜기
        else:
            GPIO.output(LED_PIN, GPIO.LOW)    # LED 끄기

    except Exception as e:
        print("센서 읽기 오류:", e)
        moisture = 0
        light = 0

    return {
        "moisture": moisture,
        "light": light
    }


    # -----------------------------
# 테스트용 메인 루프
# -----------------------------
if __name__ == "__main__":
    try:
        while True:
            # 4개 채널 모두 읽기
            ch0 = read_adc(0)
            ch1 = read_adc(1)
            ch2 = read_adc(2)
            ch3 = read_adc(3)

            print(
                f"A0={ch0:3d}  A1={ch1:3d}  A2={ch2:3d}  A3={ch3:3d}"
            )

            time.sleep(1)
    except KeyboardInterrupt:
        print("테스트 종료 (Ctrl+C)")
    finally:
        GPIO.cleanup()

