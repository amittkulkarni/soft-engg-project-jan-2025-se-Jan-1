from flask import Flask
from config import Config
from extension import db, jwt, migrate
from controller import user_routes
from flask_cors import CORS
import os

# Initialize Flask app
app = Flask(__name__)

app.config.from_object(Config)
CORS(app,origins='http://localhost:8080',supports_credentials=True)
CORS(app,origins='http://localhost:8081',supports_credentials=True)
CORS(app,resources={
         r"/*": {
             "origins": [
                 "https://seek-sage.vercel.app",
                 "http://localhost:8080",
                 "http://localhost:5000"
             ]
         }
},supports_credentials=True)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)

# Register blueprints
app.register_blueprint(user_routes)   # User routes


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
