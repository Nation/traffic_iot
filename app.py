from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

# Track the current LED state
current_state = {"state": "-", "time": "-"}


# ---- ROUTES ----

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


@app.route('/ping')
def ping():
    return "pong"


# ---- FUNCTION ----

def check_esp_status():
    try:
        r = requests.get("https://traffic-iot-test.onrender.com/ping", timeout=2)
        if r.status_code == 200 and r.text.strip() == "pong":
            return "Connected"
    except:
        pass
    return "Disconnected"


# ---- ENTRYPOINT ----

if __name__ == '__main__':
    app.run(debug=False)
