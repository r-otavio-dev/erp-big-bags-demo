from pathlib import Path
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config:
        app.config.update(test_config)
    Path(app.instance_path).mkdir(parents=True, exist_ok=True)
    db.init_app(app)
    from .routes import bp
    app.register_blueprint(bp)
    with app.app_context():
        db.create_all()
        from .services import seed_database
        seed_database()
    return app

