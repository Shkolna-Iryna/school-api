from flask import Blueprint, jsonify, request
from models import db, Task, Answer
from sqlalchemy.orm import joinedload
from flask_jwt_extended import jwt_required, get_jwt_identity

answers_bp = Blueprint("answers", __name__)

@answers_bp.route("/answers", methods=["GET"])
@jwt_required()
def get_answers():
    task_id = request.args.get("task_id", type=int)
    query = Answer.query.options(joinedload(Answer.user),  joinedload(Answer.task))
    if task_id is not None:
        query = query.filter(Answer.task_id == task_id)

    answers = query.all()
    
    answers_list = []
    for answer in answers:
        answers_list.append({
            "id": answer.id,
            "answer": answer.answer,
            "is_correct": (answer.task.correct_answer_id == answer.id) if answer.task.correct_answer_id else False,
            "user": {
                "id": answer.user.id if answer.user else None,
                "name": answer.user.name if answer.user else None
            },
            "task_id": answer.task_id
        })

    return jsonify(answers_list)

@answers_bp.route("/answers", methods=["POST"])
@jwt_required()
def create_answers():
    data = request.get_json()
    user_id = int(get_jwt_identity())

    if not data:
        return jsonify({"error": "No data"}), 400

    new_answer = Answer(
        answer=data["answer"],
        task_id=data["task_id"],
        user_id=user_id,
    )

    db.session.add(new_answer)
    db.session.commit()

    return jsonify({
        "msg": "Answer created",
        "id": new_answer.id
    }), 201

