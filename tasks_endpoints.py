from flask import Blueprint, Flask, app, current_app, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import func
import os
from errors.content_review_error import ContentNeedsReviewError
from models import Answer, db, Task
from sqlalchemy.orm import joinedload
from werkzeug.utils import secure_filename
import uuid
from flask import send_from_directory
import json

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
tasks_bp = Blueprint('tasks', __name__)  
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}

def allowed_file(filename: str) -> bool:
    if not filename:
        return False

    if "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_EXTENSIONS
UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@tasks_bp.route("/tasks", methods=["GET"])
@jwt_required()
def get_tasks():
    subject_id = request.args.get('subject_id', type=int) 
    search = request.args.get('search', type=str)
    page = request.args.get('page', default=1, type=int)
    per_page = request.args.get('per_page', default=10, type=int)

    query = Task.query.options(
        joinedload(Task.user),
    )

    if search:
        search = search.strip()
        if search:
            query = query.filter(Task.task.ilike(f"%{search}%"))

    if subject_id is not None:
        query = query.filter(Task.subject_id == subject_id)

    offset = (page - 1) * per_page
    tasks = query.order_by(Task.id.desc()).limit(per_page).offset(offset).all()

    count = query.with_entities(func.count(Task.id)).scalar() or 0
    
    items = []
    for task in tasks:
        items.append({
            "id": task.id,
            "task": task.task,
            "correct_answer_id": task.correct_answer_id,
            "image_url": json.loads(task.image_url) if task.image_url else [],
            "user": {
                "id": task.user.id if task.user else None,
                "name": task.user.name if task.user else None
            }
        })   

    return jsonify({"count":count, "items":items})
@tasks_bp.route("/tasks", methods=["POST"])
@jwt_required()
def create_task_with_photos():
    user_id = int(get_jwt_identity())

    task_text = request.form.get("task")
    subject_id = request.form.get("subject_id")
    files = request.files.getlist("photos")

    if not task_text or not subject_id:
        return jsonify({"error": "task і subject_id обовʼязкові"}), 400

    upload_folder = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_folder):
        os.makedirs(upload_folder)

    saved_files = []
    for file in files:
        if file and allowed_file(file.filename):
            ext = os.path.splitext(file.filename)[1]
            filename = secure_filename(f"{uuid.uuid4().hex}{ext}")
            path = os.path.join(upload_folder, filename)
            file.save(path)
            saved_files.append(f"{filename}")

    image_url = json.dumps(saved_files)

    # new_task створюється завжди, після циклу
    new_task = Task(
        task=task_text,
        user_id=user_id,
        subject_id=int(subject_id),
        image_url=image_url
    )

    db.session.add(new_task)
    db.session.commit()

    return jsonify({
        "msg": "Task created",
        "id": new_task.id,
        "image_url": image_url
    }), 201


@tasks_bp.route("/tasks/<int:task_id>", methods=["GET"])
@jwt_required()
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    answers = []  

    for a in task.answers:  
        answer_dict = {
            "id": a.id,
            "answer": a.answer

    }
        answers.append(answer_dict) 
    return jsonify({
        "id": task.id,
        "task": task.task,
        "user_id": task.user_id,
        "correct_answer_id": task.correct_answer_id,
        "answers": answers
    })


@tasks_bp.route("/tasks/<int:task_id>/correct", methods=["PATCH"])
@jwt_required()
def set_correct_answer(task_id):
    user_id = get_jwt_identity()

    data = request.get_json() or {}
    answer_id = data.get("answer_id")

    task = Task.query.get_or_404(task_id)

    if task.user_id != int(user_id):
        return jsonify({"error": "Only task owner can set correct answer"}), 403

    if answer_id is None:
        task.correct_answer_id = None
        db.session.commit()
        return jsonify({"ok": True, "correct_answer_id": None})

    answer = Answer.query.get_or_404(answer_id)

    if answer.task_id != task.id:
        return jsonify({"error": "Answer does not belong to this task"}), 400

    task.correct_answer_id = answer.id
    db.session.commit()

    return jsonify({"ok": True, "correct_answer_id": task.correct_answer_id})


