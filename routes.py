from flask import Blueprint, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from models import db, Exercise, Workout, WorkoutExercise
from schemas import (
    exercise_schema,
    exercises_schema,
    workout_schema,
    workouts_schema,
    workout_exercise_schema,
)

api = Blueprint("api", __name__)


def validation_error(message, status=400):
    return jsonify({"error": message}), status


@api.get("/workouts")
def get_workouts():
    workouts = Workout.query.order_by(Workout.id).all()
    return jsonify(workouts_schema.dump([
        {
            "date": w.date,
            "duration_minutes": w.duration_minutes,
            "notes": w.notes,
        }
        for w in workouts
    ]))


@api.get("/workouts/<int:workout_id>")
def get_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return validation_error("Workout not found.", 404)
    return jsonify(workout.to_dict(include_exercises=True))


@api.post("/workouts")
def create_workout():
    try:
        data = workout_schema.load(request.get_json() or {})
    except ValidationError as exc:
        return validation_error(exc.messages)

    workout = Workout(**data)
    db.session.add(workout)
    try:
        db.session.commit()
    except (ValueError, IntegrityError) as exc:
        db.session.rollback()
        return validation_error(str(exc), 400)

    return jsonify(workout.to_dict()), 201


@api.delete("/workouts/<int:workout_id>")
def delete_workout(workout_id):
    workout = db.session.get(Workout, workout_id)
    if not workout:
        return validation_error("Workout not found.", 404)

    db.session.delete(workout)
    db.session.commit()
    return jsonify({"message": "Workout deleted successfully."})


@api.get("/exercises")
def get_exercises():
    exercises = Exercise.query.order_by(Exercise.id).all()
    return jsonify(exercises_schema.dump([
        {
            "name": e.name,
            "category": e.category,
            "equipment_needed": e.equipment_needed,
        }
        for e in exercises
    ]))


@api.get("/exercises/<int:exercise_id>")
def get_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return validation_error("Exercise not found.", 404)
    return jsonify(exercise.to_dict(include_workouts=True))


@api.post("/exercises")
def create_exercise():
    try:
        data = exercise_schema.load(request.get_json() or {})
    except ValidationError as exc:
        return validation_error(exc.messages)

    exercise = Exercise(**data)
    db.session.add(exercise)
    try:
        db.session.commit()
    except (ValueError, IntegrityError) as exc:
        db.session.rollback()
        message = (
            "Exercise name must be unique."
            if isinstance(exc, IntegrityError)
            else str(exc)
        )
        return validation_error(message, 400)

    return jsonify(exercise.to_dict()), 201


@api.delete("/exercises/<int:exercise_id>")
def delete_exercise(exercise_id):
    exercise = db.session.get(Exercise, exercise_id)
    if not exercise:
        return validation_error("Exercise not found.", 404)

    db.session.delete(exercise)
    db.session.commit()
    return jsonify({"message": "Exercise deleted successfully."})


@api.post(
    "/workouts/<int:workout_id>/exercises/<int:exercise_id>/workout_exercises"
)
def add_exercise_to_workout(workout_id, exercise_id):
    workout = db.session.get(Workout, workout_id)
    exercise = db.session.get(Exercise, exercise_id)

    if not workout:
        return validation_error("Workout not found.", 404)
    if not exercise:
        return validation_error("Exercise not found.", 404)

    try:
        data = workout_exercise_schema.load(request.get_json() or {})
    except ValidationError as exc:
        return validation_error(exc.messages)

    workout_exercise = WorkoutExercise(
        workout_id=workout_id,
        exercise_id=exercise_id,
        **data,
    )
    db.session.add(workout_exercise)

    try:
        db.session.commit()
    except (ValueError, IntegrityError) as exc:
        db.session.rollback()
        message = (
            "This exercise is already attached to this workout."
            if isinstance(exc, IntegrityError)
            else str(exc)
        )
        return validation_error(message, 400)

    return jsonify(workout_exercise.to_dict(include_exercise=True)), 201
