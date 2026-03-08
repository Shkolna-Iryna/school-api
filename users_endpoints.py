from flask import Blueprint, jsonify 
from sqlalchemy import func 
from models import Answer, Task, User, db 
from flask_jwt_extended import jwt_required 
from flask import request 
from auth.decorators import roles_required

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
            User.role.label("role"),
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
            "role": u.role,
            "correct_answers": int(u.correct_answers or 0)
        }
        for u in pagination.items
    ]

    return jsonify({
        "items": users,
        "pages": pagination.pages
    })


@users_bp.route("/users", methods=["GET"])
@jwt_required()
@roles_required("admin")
def get_users():

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 10, type=int)

    query = (
        db.session.query(
            User.id,
            User.name,
            User.email,
            User.role
        )
        .order_by(User.name.asc())
    )

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    users = [
        {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role
        }
        for u in pagination.items
    ]

    return jsonify({
        "items": users,
        "pages": pagination.pages
    })

@users_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@jwt_required()
@roles_required("admin")
def change_user_role(user_id):

    data = request.get_json()

    new_role = data.get("role")

    allowed_roles = {"admin", "teacher", "student"}

    if new_role not in allowed_roles:
        return jsonify({"msg": "Invalid role"}), 400

    user = User.query.get(user_id)

    if not user:
        return jsonify({"msg": "User not found"}), 404

    user.role = new_role
    db.session.commit()

    return jsonify({
        "msg": "Role updated",
        "user": {
            "id": user.id,
            "name": user.name,
            "role": user.role
        }
    })