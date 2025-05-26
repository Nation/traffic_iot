from flask import Flask, render_template, redirect, url_for
from datetime import datetime, timedelta

app = Flask(__name__)

# Track LED state and last ping time
current_state = {"state": "-", "time": "-"}
last_heartbeat = None

@app.route('/')
def index():
    esp_status = check_esp_status()
    return render_template(
        "index.html",
        state=current_state["state"],
        time=current_state["time"],
        esp_status=esp_status
    )

@app.route('/set/<color>')
def set_color(color):
    color_map = {"R": "Red", "Y": "Yellow", "G": "Green"}
    current_state["state"] = color_map.get(color.upper(), "Unknown")
    current_state["time"] = "-"
    return redirect(url_for('index'))

@app.route('/reset')
def reset():
    current_state["state"] = "-"
    current_state["time"] = "-"
    return redirect(url_for('index'))

@app.route('/ping')  # still returns pong for basic tests
def ping():
    return "pong"

@app.route('/esp-heartbeat')
def esp_heartbeat():
    global last_heartbeat
    last_heartbeat = datetime.utcnow()
    return "ok"

def check_esp_status():
    if last_heartbeat and (datetime.utcnow() - last_heartbeat) < timedelta(seconds=30):
        return "Connected"
    return "Disconnected"

if __name__ == '__main__':
    app.run(debug=False)
