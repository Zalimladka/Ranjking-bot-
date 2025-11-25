import os
import re
import json
import uuid
import hashlib
import logging
from flask import Flask, request, redirect, url_for, render_template, make_response, abort

class Config:
    ADMIN_PATH = "/admin-ZalimXRDX"
    ADMIN_PASSWORD_HASH = "e4d909c290d0fb1ca068ffaddf22cbd0"
    START_URL = "http://de3.bot-hosting.net:8000/"

app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def get_or_set_device_cookie():
    device_id = request.cookies.get("device_id")
    if not device_id:
        device_id = str(uuid.uuid4())
    resp = make_response()
    resp.set_cookie("device_id", device_id, max_age=60*60*24*365*10, httponly=True, samesite="Lax")
    return device_id, resp

def is_admin(password: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == Config.ADMIN_PASSWORD_HASH

@app.route("/", methods=["GET", "POST"])
def index():
    try:
        device_id = request.cookies.get("device_id")
        if not device_id:
            device_id = str(uuid.uuid4())
        if request.method == "POST":
            pass
        status = "approved"
        resp = make_response(render_template("home.html",
                           device_id=device_id,
                           status=status,
                           start_url=Config.START_URL))
        resp.set_cookie("device_id", device_id, max_age=60*60*24*365*10, httponly=True, samesite="Lax")
        return resp
    except Exception as e:
        logging.error(f"Index error: {e}")
        abort(500)

@app.route(Config.ADMIN_PATH, methods=["GET", "POST"])
def admin_panel():
    try:
        if request.method == "POST":
            password = request.form.get("password", "")
            if not is_admin(password):
                return render_template("admin.html", logged_in=False)
            device_id = request.cookies.get("device_id")
            if not device_id:
                device_id = str(uuid.uuid4())
            return render_template(
                "admin.html",
                logged_in=True,
                device_id=device_id,
                status="approved",
                admin_password=password
            )
        return render_template("admin.html", logged_in=False)
    except Exception as e:
        logging.error(f"Admin panel error: {e}")
        abort(500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
    
