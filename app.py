from flask import Flask, render_template, send_from_directory, session, redirect
from routes.report_routes import report_bp
from routes.auth_routes import auth_bp
from utils.auth import login_required
from pymongo import MongoClient
from werkzeug.security import generate_password_hash



app = Flask(__name__)

#  Secret key (for session)
app.secret_key = "supersecretkey"

# ------------------ DATABASE ------------------
client = MongoClient("mongodb://localhost:27017/")
db = client["qr_reports_db"]
users = db["users"]


# ------------------ MASTER ADMIN ------------------
def create_admin():
    if not users.find_one({"username": "admin"}):
        users.insert_one({
            "username": "admin",
            "password": generate_password_hash("admin123"),
            "role": "admin"
        })
        print("✅ Admin created: admin / admin123")


# ------------------ BLUEPRINTS ------------------
app.register_blueprint(report_bp)
app.register_blueprint(auth_bp)


# ------------------ FILE DOWNLOAD ------------------
@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory('uploads', filename)


# ------------------ MAIN PAGES ------------------

@app.route("/")
@login_required
def dashboard():
    return render_template("home/dashboard.html")


@app.route("/upload")
@login_required
def upload_page():
    return render_template("upload.html")


@app.route("/search")
@login_required
def search_page():
    return render_template("search.html", role=session.get("role"))


@app.route("/edit/<document_id>")
@login_required
def edit_page(document_id):
    return render_template("edit.html", document_id=document_id)


# ------------------ AUTH PAGES ------------------

@app.route("/login")
def login():
    return render_template("accounts/login.html")


@app.route("/register")
def register():
    return render_template("accounts/register.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

@app.route("/admin/report-types")
def report_types():
    return render_template("admin/manage_dropdown.html", field="report_type")

@app.route("/admin/divisions")
def divisions():
    return render_template("admin/manage_dropdown.html", field="division")

@app.route("/admin/equipment")
def equipment():
    return render_template("admin/manage_dropdown.html", field="equipment")


# ------------------ ERROR PAGES ------------------

@app.route("/404")
def error_404():
    return render_template("home/page-404.html")


@app.route("/500")
def error_500():
    return render_template("home/page-500.html")

# drodown options

@app.route("/admin/report-types")
def manage_report_types():
    return render_template("admin/manage_dropdown.html", field="report_type")

@app.route("/admin/divisions")
def manage_divisions():
    return render_template("admin/manage_dropdown.html", field="division")

@app.route("/admin/equipment")
def manage_equipment():
    return render_template("admin/manage_dropdown.html", field="equipment")


# ------------------ RUN ------------------

if __name__ == "__main__":
    app.run(debug=True)