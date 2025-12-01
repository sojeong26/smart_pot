from flask import Flask, render_template, jsonify
from sensor import get_sensor_data, pump_on, pump_off
import time

app = Flask(__name__)


# -----------------------------
# 메인 페이지
# -----------------------------
@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/status")
def status():
    return render_template("status.html")


# -----------------------------
# API — 센서 값 반환
# -----------------------------
@app.route("/api/sensor")
def api_sensor():
    data = get_sensor_data()
    return jsonify(data)


# -----------------------------
# API — 물 주기 실행
# -----------------------------
@app.route("/api/water")
def api_water():
    pump_on()
    time.sleep(3)     # 3초간 물 주기
    pump_off()
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
