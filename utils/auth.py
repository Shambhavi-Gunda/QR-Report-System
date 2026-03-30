from flask import session, redirect


# 🔐 Check if user is logged in
def login_required(func):
    def wrapper(*args, **kwargs):
        if "user" not in session:
            return redirect("/login")
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper


# 🔒 Check if user is admin
def admin_required(func):
    def wrapper(*args, **kwargs):
        if session.get("role") != "admin":
            return "Access Denied (Admin only)", 403
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper