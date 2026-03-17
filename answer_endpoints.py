import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
import json
from models import Answer, db
from sqlalchemy.orm import joinedload


ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename: str) -> bool:
    if not filename:
        return False
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower() 
    return ext in ALLOWED_EXTENSIONS

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

answers_bp = Blueprint('answers', __name__)
@answers_bp.route("/answers", methods=["GET"])
@jwt_required()
def get_answers():
    task_id = request.args.get("task_id", type=int)

    query = Answer.query.options(
        joinedload(Answer.user),
        joinedload(Answer.task)
    )

    if task_id is not None:
        query = query.filter(Answer.task_id == task_id)

    answers = query.all()

    answers_list = []

    for answer in answers:

        is_correct = False
        if answer.task and answer.task.correct_answer_id:
            is_correct = answer.task.correct_answer_id == answer.id

        answers_list.append({
            "id": answer.id,
            "answer": answer.answer,
            "is_correct": is_correct,
            "user": {
                "id": answer.user.id if answer.user else None,
                "name": answer.user.name if answer.user else None,
                "role": answer.user.role if answer.user.role else None
            },
            "task_id": answer.task_id,
            "image_url": json.loads(answer.image_url) if answer.image_url else [],
            "voice_url": answer.voice_url 

        })

    return jsonify(answers_list)


@answers_bp.route("/answers", methods=["POST"])
@jwt_required()
def create_answers_with_photos():
    user_id = int(get_jwt_identity())

    answer_text = request.form.get("answer")
    task_id = request.form.get("task_id")
    files = request.files.getlist("photos")
    voice_files = request.files.getlist("voice")  

    if not answer_text or not task_id:
        return jsonify({"error": "answer і task_id є обовʼязковими"}), 400

    upload_folder = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_folder, exist_ok=True)

    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{uuid.uuid4().hex}{ext}")
            file.save(os.path.join(upload_folder, filename))
            saved_files.append(filename)
    image_url = json.dumps(saved_files)

    voice_url = None
    if voice_files:
        voice_file = voice_files[0]
        if voice_file.filename != "":
            ext = os.path.splitext(voice_file.filename)[1]
            filename = secure_filename(f"{uuid.uuid4().hex}{ext}")
            voice_file.save(os.path.join(upload_folder, filename))
            voice_url = filename

    new_answer = Answer(
        answer=answer_text,
        task_id=task_id,
        user_id=user_id,
        image_url=image_url,
        voice_url=voice_url  # додано
    )

    db.session.add(new_answer)
    db.session.commit()

    return jsonify({
        "msg": "Відповідь створена",
        "id": new_answer.id,
        "image_url": image_url,
        "voice_url": voice_url
    }), 201

@answers_bp.route("/answers/<int:answer_id>", methods=["DELETE"])
@jwt_required()
def delete_answer(answer_id):
    user_id = int(get_jwt_identity())
    claims = get_jwt()
    role = claims.get("role", "user")  # роль з токена

    answer = Answer.query.get_or_404(answer_id)

    # Перевірка: власник або адмін
    if answer.user_id != user_id and role != "admin":
        return jsonify({"error": "Only answer owner or admin can delete this answer"}), 403

    # Видалення збережених файлів відповіді
    upload_folder = os.path.join(os.getcwd(), "uploads")

    if answer.image_url:
        try:
            images = json.loads(answer.image_url)
            for img_filename in images:
                path = os.path.join(upload_folder, img_filename)
                if os.path.exists(path):
                    os.remove(path)
        except Exception as e:
            print(f"Error deleting answer images: {e}")

    # Якщо є voice_url у відповіді, теж видаляємо
    if getattr(answer, "voice_url", None):
        path = os.path.join(upload_folder, answer.voice_url)
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                print(f"Error deleting answer voice file: {e}")

    # Видалення запису з бази
    db.session.delete(answer)
    db.session.commit()

    return jsonify({"msg": f"Answer {answer_id} deleted"}), 200
