from flask import Blueprint, jsonify
from sqlalchemy import func
from models import Answer, Task, User, db
from flask_jwt_extended import jwt_required

users_bp = Blueprint("users", __name__)

@users_bp.route("/rating", methods=["GET"])
@jwt_required()
def get_rating():
    correct_count = func.count(Task.correct_answer_id)

    rows = (
        db.session.query(
            User.id.label("user_id"),
            User.name.label("name"),
            User.email.label("email"),
            correct_count.label("correct_answers")
        )
        .outerjoin(Answer, Answer.user_id == User.id)
        .outerjoin(Task, Task.correct_answer_id == Answer.id)
        .group_by(User.id)
        .order_by(correct_count.desc(), User.name.asc())
        .all()
    )

    return jsonify([
        {
            "user_id": r.user_id,
            "name": r.name,
            "email": r.email,
            "correct_answers": int(r.correct_answers or 0)
        }
        for r in rows
    ])