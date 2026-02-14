from flask import Blueprint, jsonify 
from sqlalchemy import func 
from models import Answer, Task, User, db 
from flask_jwt_extended import jwt_required 
from flask import request 

users_bp = Blueprint("users", __name__)

@users_bp.route("/rating", methods=["GET"])
@jwt_required()
def get_rating_paginated():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    correct_count = func.count(Task.correct_answer_id)

    query = (
        db.session.query(
            User.id.label("user_id"),
            User.name.label("name"),
            correct_count.label("correct_answers")
        )
        .outerjoin(Answer, Answer.user_id == User.id)
        .outerjoin(Task, Task.correct_answer_id == Answer.id)
        .group_by(User.id)
        .order_by(correct_count.desc(), User.name.asc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    users = [
        {
            "user_id": u.user_id,
            "name": u.name,
            "correct_answers": int(u.correct_answers or 0)
        }
        for u in pagination.items
    ]

    return jsonify({
        "items": users,
        "pages": pagination.pages
    })
