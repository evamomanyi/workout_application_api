from marshmallow import Schema, fields, validate, validates_schema, ValidationError


class ExerciseSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    category = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    equipment_needed = fields.Bool(required=True)


class WorkoutSchema(Schema):
    date = fields.Date(required=True)
    duration_minutes = fields.Int(
        required=True,
        validate=validate.Range(min=0),
    )
    notes = fields.Str(allow_none=True)


class WorkoutExerciseSchema(Schema):
    reps = fields.Int(allow_none=True, validate=validate.Range(min=1))
    sets = fields.Int(allow_none=True, validate=validate.Range(min=1))
    duration_seconds = fields.Int(
        allow_none=True,
        validate=validate.Range(min=1),
    )

    @validates_schema
    def validate_training_data(self, data, **kwargs):
        if not any(
            data.get(field) is not None
            for field in ("reps", "sets", "duration_seconds")
        ):
            raise ValidationError(
                "Provide at least one of reps, sets, or duration_seconds."
            )

        if data.get("reps") is not None and data.get("sets") is None:
            raise ValidationError(
                "When reps are provided, sets must also be provided."
            )


exercise_schema = ExerciseSchema()
exercises_schema = ExerciseSchema(many=True)

workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)

workout_exercise_schema = WorkoutExerciseSchema()
