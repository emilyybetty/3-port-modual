from flask import Flask, render_template, request, redirect, url_for, jsonify
import time
import random
import string
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Rate limiting to prevent abuse
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# In-memory storage for redirection settings
redirection_settings = {
    "active": False,
    "redirect_url": "",
    "decline_url": "",
    "timer": 0,
    "password": ""
}

# Generate a random string for dynamic links
def generate_random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Home route
@app.route('/')
def home():
    return render_template('index.html', settings=redirection_settings)

# Update redirection settings
@app.route('/update_settings', methods=['POST'])
def update_settings():
    data = request.json
    redirection_settings["active"] = data.get("active", False)
    redirection_settings["redirect_url"] = data.get("redirect_url", "")
    redirection_settings["decline_url"] = data.get("decline_url", "")
    redirection_settings["timer"] = int(data.get("timer", 0))
    redirection_settings["password"] = data.get("password", "")
    return jsonify({"status": "success", "settings": redirection_settings})

# Dynamic redirection route
@app.route('/redirect')
def dynamic_redirect():
    if not redirection_settings["active"]:
        return "Redirection is currently deactivated."

    # Check for bot (simple captcha)
    if not request.args.get("captcha") == "valid":
        return redirect(redirection_settings["decline_url"])

    # Timer-based redirection
    time.sleep(redirection_settings["timer"])
    return redirect(redirection_settings["redirect_url"])

# Bot checker captcha route
@app.route('/captcha')
def captcha():
    return render_template('captcha.html')

# Validate captcha
@app.route('/validate_captcha', methods=['POST'])
def validate_captcha():
    user_input = request.form.get("captcha_input")
    if user_input == "1234":  # Simple static captcha for demonstration
        return jsonify({"status": "success", "redirect_url": url_for('dynamic_redirect', captcha="valid")})
    return jsonify({"status": "failure"})

# Password protection route
@app.route('/protected')
def protected():
    return render_template('protected.html')

# Validate password
@app.route('/validate_password', methods=['POST'])
def validate_password():
    user_password = request.form.get("password")
    if user_password == redirection_settings["password"]:
        return jsonify({"status": "success"})
    return jsonify({"status": "failure"})

if __name__ == '__main__':
    app.run(debug=True)
