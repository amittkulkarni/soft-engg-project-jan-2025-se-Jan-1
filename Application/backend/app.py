from flask import Flask
from config import Config
from extension import db, jwt, migrate
from controller import user_routes

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
jwt.init_app(app)
migrate.init_app(app, db)

# Register blueprints
app.register_blueprint(user_routes, url_prefix='/api')   # User routes


if __name__ == '__main__':
    app.run(debug=True)
