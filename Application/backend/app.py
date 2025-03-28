from flask import Flask
from config import Config
from extension import db, jwt, migrate
from controller import user_routes
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)

app.config.from_object(Config)
CORS(app,origins='http://localhost:8080',supports_credentials=True)
CORS(app,origins='http://localhost:8081',supports_credentials=True)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)

# Register blueprints
app.register_blueprint(user_routes)   # User routes

# Vercel serverless function handler
def handler(event, context):
    return app(event, context)


if __name__ == '__main__':
    app.run(debug=True, port=5000)
