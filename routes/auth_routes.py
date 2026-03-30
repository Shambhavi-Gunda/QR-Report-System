from flask import Blueprint, request, jsonify, session
from config import users_collection
from models.user_model import create_user, verify_password

auth_bp = Blueprint("auth", __name__)


# ---------------- REGISTER ----------------
@auth_bp.route("/api/register", methods=["POST"])
def register():

    try:
        data = request.json

        #  Required fields (NO EMAIL now)
        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400

        #  Check existing user
        if users_collection.find_one({"username": data["username"]}):
            return jsonify({"error": "User already exists"}), 409

        #  Create user (role = user)
        user = create_user({
            "username": data["username"],
            "password": data["password"],
            "role": "user"
        })

        users_collection.insert_one(user)

        return jsonify({"message": "User registered successfully"}), 201

    except Exception as e:
        print("REGISTER ERROR:", e)
        return jsonify({"error": "Server error"}), 500


# ---------------- LOGIN ----------------
@auth_bp.route("/api/login", methods=["POST"])
def login():

    try:
        data = request.json

        if not data.get("username") or not data.get("password"):
            return jsonify({"error": "Username and password required"}), 400

        #  Find user
        user = users_collection.find_one({"username": data["username"]})

        if not user or not verify_password(user, data["password"]):
            return jsonify({"error": "Invalid credentials"}), 401

        #  Store session
        session["user"] = user["username"]
        session["role"] = user["role"]

        #  Remember me
        if data.get("remember"):
            session.permanent = True
        else:
            session.permanent = False

        return jsonify({
            "message": "Login successful",
            "username": user["username"],
            "role": user["role"]
        }), 200

    except Exception as e:
        print("LOGIN ERROR:", e)
        return jsonify({"error": "Server error"}), 500