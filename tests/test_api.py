from datetime import date

import 

from app import app
from models import db, Exercise, Workout


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    with app.app_context():
        db.drop_all()
        db.create_all()
        yield app.test_client()
        db.session.remove()
        db.drop_all()


def test_create_exercise(client):
    response = client.post(
        "/exercises",
        json={
            "name": "Deadlift",
            "category": "Strength",
            "equipment_needed": True,
        },
    )
    assert response.status_code == 201
    assert response.get_json()["name"] == "Deadlift"


def test_exercise_schema_rejects_empty_name(client):
    response = client.post(
        "/exercises",
        json={
            "name": "",
            "category": "Strength",
            "equipment_needed": False,
        },
    )
    assert response.status_code == 400


def test_create_workout_and_attach_exercise(client):
    exercise = client.post(
        "/exercises",
        json={
            "name": "Plank",
            "category": "Core",
            "equipment_needed": False,
        },
    ).get_json()

    workout = client.post(
        "/workouts",
        json={
            "date": "2026-08-30",
            "duration_minutes": 20,
            "notes": "Core session",
        },
    ).get_json()

    response = client.post(
        f"/workouts/{workout['id']}/exercises/{exercise['id']}/workout_exercises",
        json={"sets": 3, "duration_seconds": 60},
    )
    assert response.status_code == 201
    assert response.get_json()["exercise"]["name"] == "Plank"


def test_workout_schema_rejects_negative_duration(client):
    response = client.post(
        "/workouts",
        json={
            "date": "2026-08-30",
            "duration_minutes": -5,
            "notes": "Invalid",
        },
    )
    assert response.status_code == 400
