import os
import re
import json
import uuid
import hashlib
import logging
import requests
from flask import Flask, request, redirect, url_for, render_template, make_response, abort

# ====================================================
# CONFIGURATION
# ====================================================
class Config:
    ADMIN_PATH = "/admin-ZalimXRDX"  # Changed to your name
    # hash of "RAVIRAJ@123" -> keep same
    ADMIN_PASSWORD_HASH = "e4d909c290d0fb1ca068ffaddf22cbd0"  # Hash for "RAVIRAJ@123"
    START_URL = "http://fi6.bot-hosting.net:21240/"

# ====================================================
# APP SETUP
# ====================================================
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# ====================================================
# UTILS
# ====================================================
def get_or_set_device_cookie():
    device_id = request.cookies.get("device_id")
    if not device_id:
        device_id = str(uuid.uuid4())
    resp = make_response()
    resp.set_cookie("device_id", device_id, max_age=60*60*24*365*10, httponly=True, samesite="Lax")
    return device_id, resp

def is_admin(password: str) -> bool:
    return hashlib.sha256(password.encode()).hexdigest() == Config.ADMIN_PASSWORD_HASH

# ====================================================
# ROUTES
# ====================================================
@app.route("/", methods=["GET", "POST"])
def index():
    try:
        device_id = request.cookies.get("device_id")
        if not device_id:
            device_id = str(uuid.uuid4())
        if request.method == "POST":
            # No approval needed - direct approved
            pass  # Skip old logic
        # Always approved - no checks
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
            if not is_admin(request.form.get("password", "")):
                return render_template("admin.html", logged_in=False)
            # Simple panel - show current device (no pending/approved/rejected)
            device_id = request.cookies.get("device_id")
            if not device_id:
                device_id = str(uuid.uuid4())
            return render_template(
                "admin.html",
                logged_in=True,
                device_id=device_id,
                status="approved",  # Always
                admin_password=request.form.get("password")
            )
        return render_template("admin.html", logged_in=False)
    except Exception as e:
        logging.error(f"Admin panel error: {e}")
        abort(500)

# Admin routes removed - no approve/reject needed

# ====================================================
# ENTRY POINT
# ====================================================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
