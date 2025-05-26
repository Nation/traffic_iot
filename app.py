from flask import Flask, render_template, redirect, url_for
import requests

app = Flask(__name__)

# Replace with your ESP8266's IP address
ESP_IP = 'http://192.168.1.42'  # Example: adjust to match your network

# Simple state tracking (optional)
current_state = {"state": "-", "time": "-"}

# Check if ESP8266 is reachable
def check_esp_status():
    try:
        response = requests.get(f"{ESP_IP}/ping", timeout=1)
        if response.status_code == 200:
            return "Connected"
    except:
        pass
    return "Disconnected"

# Home route
@app.route('/')
def index():
    esp_status = check_esp_status()
    return render_template("index.html", state=current_state["state"], time=current_state["time"], esp_status=esp_status)

# Control routes
@app.route('/set/<color>')
def set_color(color):
    try:
        if color == "R":
            requests.get(f"{ESP_IP}/led?r=1&y=0&g=0")
            current_state["state"] = "Red"
        elif color == "Y":
            requests.get(f"{ESP_IP}/led?r=0&y=1&g=0")
            current_state["state"] = "Yellow"
        elif color == "G":
            requests.get(f"{ESP_IP}/led?r=0&y=0&g=1")
            current_state["state"] = "Green"
        current_state["time"] = "-"
    except:
        current_state["state"] = "Error"
        current_state["time"] = "N/A"
    return redirect(url_for("index"))

@app.route('/reset')
def reset():
    try:
        requests.get(f"{ESP_IP}/led?r=0&y=0&g=0")
        current_state["state"] = "-"
        current_state["time"] = "-"
    except:
        current_state["state"] = "Error"
        current_state["time"] = "N/A"
    return redirect(url_for("index"))

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
