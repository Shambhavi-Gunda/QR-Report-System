from flask import Blueprint, request, jsonify
from config import users_collection
from models.user_model import create_user, verify_password

auth_bp = Blueprint("auth", __name__)

# Register API

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json

    required_fields = ["username", "email", "password"]
    for field in required_fields:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if users_collection.find_one({"email": data["email"]}):
        return jsonify({"error": "User already exists"}), 409

    user = create_user(data)
    users_collection.insert_one(user)

    return jsonify({"message": "User registered successfully"}), 201


# Login API

@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json

    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = users_collection.find_one({"email": data["email"]})

    if not user or not verify_password(user, data["password"]):
        return jsonify({"error": "Invalid credentials"}), 401

    return jsonify({
        "message": "Login successful",
        "username": user["username"],
        "role": user["role"]
    }), 200
