from werkzeug.security import generate_password_hash, check_password_hash

def create_user(data):
    return {
        "username": data["username"],
        "email": data["email"],
        "password": generate_password_hash(data["password"]),
        "role": data.get("role", "viewer"),
        "active": True
    }

def verify_password(user, password):
    return check_password_hash(user["password"], password)
