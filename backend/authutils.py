# SETUP: Imports
import jwt
from flask import request, jsonify
from functools import wraps
from datetime import datetime, timedelta
from dba import User, ROLE_ADMIN, ROLE_DOCTOR, ROLE_PATIENT
from dba import db
import os

SECRET_KEY = os.environ.get("SECRET_KEY", "my-fallback-secret-key")

# FUNCTION: Create JWT
def create_token(user):
    payload = {
        "id": user.id,
        "username": user.username,
        "role": user.role,
        "exp": datetime.utcnow() + timedelta(hours=6)
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


# FUNCTION: Decode JWT
def decode_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except:
        return None


# ROLE: Authentication decorator
def require_auth(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        # INPUT: Authorization header
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or invalid token"}), 401

        token = auth_header.split(" ")[1]
        data = decode_token(token)

        if not data:
            return jsonify({"error": "Token expired or invalid"}), 401

        request.current_user = User.query.get(data["id"])
        return f(*args, **kwargs)
    return wrapper


# ROLE: Admin-only access
def admin_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = request.current_user
        if user.role != ROLE_ADMIN:
            return jsonify({"error": "Admin access required"}), 403
        return f(*args, **kwargs)
    return wrapper


# ROLE: Doctor-only access
def doctor_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = request.current_user
        if user.role != ROLE_DOCTOR:
            return jsonify({"error": "Doctor access required"}), 403
        return f(*args, **kwargs)
    return wrapper


# ROLE: Patient-only access
def patient_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        user = request.current_user
        if user.role != ROLE_PATIENT:
            return jsonify({"error": "Patient access required"}), 403
        return f(*args, **kwargs)
    return wrapper
