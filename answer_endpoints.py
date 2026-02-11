import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
from models import Answer, db
from sqlalchemy.orm import joinedload


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()  # Отримуємо розширення файлу
    return ext in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

answers_bp = Blueprint('answers', __name__)
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
def create_answers_with_photos():

    user_id = int(get_jwt_identity())

    answer_text = request.form.get("answer")
    task_id = request.form.get("task_id")
    files = request.files.getlist("photos")

    # answer_text = data.get("answer")
    # task_id = data.get("task_id")
    # files = request.files.getlist("photos")

    if not answer_text or not task_id:
        return jsonify({"error": "answer і task_id є обовʼязковими"}), 400

    upload_folder = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{uuid.uuid4().hex}{ext}")
            path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(path)
            saved_files.append(f"{filename}")

    image_url = json.dumps(saved_files)

    new_answer = Answer(
        answer=answer_text,
        task_id=task_id,
        user_id=user_id,
        image_url=image_url  # Зберігаємо шляхи до файлів у базі даних
    )

    db.session.add(new_answer)
    db.session.commit()

    return jsonify({
        "msg": "Відповідь створена",
        "id": new_answer.id,
        "image_url": image_url
    }), 201
