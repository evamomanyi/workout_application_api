from datetime import date

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint
from sqlalchemy.orm import validates

db = SQLAlchemy(


class Exercise(db.Model):
    __tablename__ = "exercises"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    category = db.Column(db.String(50), nullable=False)
    equipment_needed = db.Column(db.Boolean, nullable=False, default=False)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="exercise",
        cascade="all, delete-orphan",
    )

    workouts = db.relationship(
        "Workout",
        secondary="workout_exercises",
        primaryjoin="Exercise.id == WorkoutExercise.exercise_id",
        secondaryjoin="Workout.id == WorkoutExercise.workout_id",
        viewonly=True,
    )

    @validates("name")
    def validate_name(self, key, value):
        value = value.strip() if isinstance(value, str) else value
        if not value:
            raise ValueError("Exercise name cannot be empty.")
        if len(value) > 100:
            raise ValueError("Exercise name cannot exceed 100 characters.")
        return value

    @validates("category")
    def validate_category(self, key, value):
        value = value.strip() if isinstance(value, str) else value
        if not value:
            raise ValueError("Exercise category cannot be empty.")
        if len(value) > 50:
            raise ValueError("Exercise category cannot exceed 50 characters.")
        return value

    def to_dict(self, include_workouts=False):
        data = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "equipment_needed": self.equipment_needed,
        }
        if include_workouts:
            data["workouts"] = [
                {"id": w.id, "date": w.date.isoformat()}
                for w in self.workouts
            ]
        return data


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False, default=date.today)
    duration_minutes = db.Column(db.Integer, nullable=False)
    notes = db.Column(db.Text, nullable=True)

    workout_exercises = db.relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
    )

    exercises = db.relationship(
        "Exercise",
        secondary="workout_exercises",
        primaryjoin="Workout.id == WorkoutExercise.workout_id",
        secondaryjoin="Exercise.id == WorkoutExercise.exercise_id",
        viewonly=True,
    )

    __table_args__ = (
        CheckConstraint(
            "duration_minutes >= 0",
            name="ck_workout_duration_nonnegative",
        ),
    )

    @validates("duration_minutes")
    def validate_duration(self, key, value):
        if not isinstance(value, int) or isinstance(value, bool):
            raise ValueError("Duration must be an integer.")
        if value < 0:
            raise ValueError("Duration cannot be negative.")
        return value

    def to_dict(self, include_exercises=False):
        data = {
            "id": self.id,
            "date": self.date.isoformat(),
            "duration_minutes": self.duration_minutes,
            "notes": self.notes,
        }
        if include_exercises:
            data["exercises"] = [
                we.to_dict(include_exercise=True)
                for we in self.workout_exercises
            ]
        return data


class WorkoutExercise(db.Model):
    __tablename__ = "workout_exercises"

    id = db.Column(db.Integer, primary_key=True)
    workout_id = db.Column(
        db.Integer,
        db.ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id = db.Column(
        db.Integer,
        db.ForeignKey("exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    duration_seconds = db.Column(db.Integer, nullable=True)

    workout = db.relationship("Workout", back_populates="workout_exercises")
    exercise = db.relationship("Exercise", back_populates="workout_exercises")

    __table_args__ = (
        UniqueConstraint(
            "workout_id",
            "exercise_id",
            name="uq_workout_exercise_pair",
        ),
        CheckConstraint(
            "reps IS NULL OR reps > 0",
            name="ck_workout_exercise_reps_positive",
        ),
        CheckConstraint(
            "sets IS NULL OR sets > 0",
            name="ck_workout_exercise_sets_positive",
        ),
        CheckConstraint(
            "duration_seconds IS NULL OR duration_seconds > 0",
            name="ck_workout_exercise_duration_positive",
        ),
    )

    @validates("reps", "sets", "duration_seconds")
    def validate_positive_values(self, key, value):
        if value is not None:
            if not isinstance(value, int) or isinstance(value, bool):
                raise ValueError(f"{key} must be an integer.")
            if value <= 0:
                raise ValueError(f"{key} must be greater than zero.")
        return value

    def to_dict(self, include_exercise=False):
        data = {
            "id": self.id,
            "workout_id": self.workout_id,
            "exercise_id": self.exercise_id,
            "reps": self.reps,
            "sets": self.sets,
            "duration_seconds": self.duration_seconds,
        }
        if include_exercise:
            data["exercise"] = self.exercise.to_dict()
        return data
