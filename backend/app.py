from flask import Flask
from routes.residents import residents_bp
from routes.caregivers import caregivers_bp
from routes.assignment import assignments_bp
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# 🔹 JWT Configuration
app.config["JWT_SECRET_KEY"] = "your_secret_key"
jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(residents_bp)
app.register_blueprint(caregivers_bp)
app.register_blueprint(assignments_bp)

if __name__ == '__main__':
    app.run(debug=True)
