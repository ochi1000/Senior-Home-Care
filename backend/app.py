from flask import Flask
from routes.residents import residents_bp
from routes.caregivers import caregivers_bp
from routes.assignment import assignments_bp
from routes.schedules import schedules_bp
from flask_jwt_extended import JWTManager
from routes.auth import auth_bp
from flask_cors import CORS
from datetime import timedelta

app = Flask(__name__)

CORS(app)

# 🔹 JWT Configuration
app.config["JWT_SECRET_KEY"] = "9a99dbeee967a05637bfeb55f4fa34f359d951f2679f81a805c815f8c94fdaf8d207e6206cc7fd679de2af87b44fda1919372e9b7b3abe314baab4a5f8fb9c326dcd1361c1cdf099e657f5a61564c4906b633c0ed4c9e4470e1fa7dcfd6e670592494a6112acf0104d1420caa0191e36b99f5957a601438fb697375c29461c0ed9675d95362343759c0425dbc19f649e6ceb98475eec1c7597ae45d00d3da3b0dd5af4cda1c86b10325cf522ffaaa19d936a53e30e557b6d8fca8b77a8a8c93282c4d704b008ea2453f1dce3f9d0498b5e921ac45b1080090c4ffe12b912500f2a85eb0ab7ea21aca84cd19716d4040067e6ecf3affb5f1e0c76750bcd2a4fde"
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)

jwt = JWTManager(app)

# Register Blueprints
app.register_blueprint(auth_bp)
app.register_blueprint(residents_bp)
app.register_blueprint(caregivers_bp)
app.register_blueprint(assignments_bp)
app.register_blueprint(schedules_bp)

if __name__ == '__main__':
    app.run(debug=True)
