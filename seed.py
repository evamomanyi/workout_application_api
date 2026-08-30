from datetime import date

from app import app
from models import db, Exercise, Workout, WorkoutExercise


with app.app_context():
    # Reset seeded data so this script can be safely rerun.
    WorkoutExercise.query.delete()
    Workout.query.delete()
    Exercise.query.delete()
    db.session.commit()

    pushups = Exercise(
        name="Push-ups",
        category="Strength",
        equipment_needed=False,
    )
    squats = Exercise(
        name="Squats",
        category="Strength",
        equipment_needed=False,
    )
    running = Exercise(
        name="Running",
        category="Cardio",
        equipment_needed=False,
    )
    bench_press = Exercise(
        name="Bench Press",
        category="Strength",
        equipment_needed=True,
    )

    workout1 = Workout(
        date=date(2026, 8, 25),
        duration_minutes=45,
        notes="Upper body strength session",
    )
    workout2 = Workout(
        date=date(2026, 8, 27),
        duration_minutes=35,
        notes="Lower body and cardio",
    )

    db.session.add_all([
        pushups, squats, running, bench_press, workout1, workout2
    ])
    db.session.flush()

    db.session.add_all([
        WorkoutExercise(
            workout=workout1,
            exercise=pushups,
            reps=12,
            sets=3,
        ),
        WorkoutExercise(
            workout=workout1,
            exercise=bench_press,
            reps=10,
            sets=4,
        ),
        WorkoutExercise(
            workout=workout2,
            exercise=squats,
            reps=15,
            sets=3,
        ),
        WorkoutExercise(
            workout=workout2,
            exercise=running,
            duration_seconds=1200,
        ),
    ])

    db.session.commit()
    print("Database seeded successfully.")
