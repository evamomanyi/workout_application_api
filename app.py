from flask import Flask
from flask_migrate import Migrate
from models import db
from routes import api

app = Flask(__name__
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
Migrate(app, db)

app.register_blueprint(api)


@app.get("/")
def index():
    return {
        "message": "Workout API is running",
        "endpoints": {
            "workouts": "/workouts",
            "exercises": "/exercises",
            "health": "/health",
        },
    }


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    app.run(port=5555, debug=True)
