#!/usr/bin/env python3
"""Pentest.TV SSO token service. HS256 JWT signed with a weak secret (crackable).
Get a user token at /login, forge an admin token after cracking the secret, read the
flag at /admin. The flag is per deploy, read from the shared svc_flags volume."""
import os
import jwt
from flask import Flask, request, jsonify

app = Flask(__name__)
SECRET = os.environ.get("JWT_SECRET", "Summer2024")   # deliberately weak; in the lab wordlist


def flag():
    try:
        return open("/svc/jwt_flag.txt").read().strip()
    except Exception:
        return "PENTESTTV{flag-not-planted}"


@app.route("/")
def index():
    return ("Pentest.TV SSO.\n"
            "GET /login for a token. GET /admin with 'Authorization: Bearer <token>'.\n")


@app.route("/login", methods=["GET", "POST"])
def login():
    token = jwt.encode({"user": "guest", "role": "user"}, SECRET, algorithm="HS256")
    return jsonify({"token": token})


@app.route("/admin")
def admin():
    auth = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    try:
        data = jwt.decode(auth, SECRET, algorithms=["HS256"])
    except Exception as e:
        return jsonify({"error": f"invalid token: {e}"}), 401
    if data.get("role") == "admin":
        return jsonify({"flag": flag()})
    return jsonify({"error": "admin role required; forge a token with role=admin"}), 403


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
