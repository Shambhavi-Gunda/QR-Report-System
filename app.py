from flask import Flask
from routes.report_routes import report_bp
from routes.auth_routes import auth_bp


app = Flask(__name__)
app.config['SECRET_KEY'] = 'qr-secret-key'

@app.route("/")
def home():
    return "QR Report System Backend is Running"

app.register_blueprint(report_bp) # attaches all routes inside report_bp to this app
app.register_blueprint(auth_bp)


if __name__ == "__main__":
    app.run(debug=True)
