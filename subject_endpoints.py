from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from models import Subject, db

subjects_bp = Blueprint("subjects", __name__)

@subjects_bp.route("/subjects", methods=["POST"])
@jwt_required()
def create_subject():
    data = request.get_json()

    if not data or "title" not in data:
        return jsonify({"error": "Поле 'title' є обовʼязковим"}), 400

    new_subject = Subject(
        title=data["title"]
    )

    db.session.add(new_subject)
    db.session.commit()

    return jsonify({
        "title": new_subject.title
    }), 201


@subjects_bp.route("/subjects", methods=["GET"])
@jwt_required()
def get_subjects():
    subjects = Subject.query.all()
    subjects_list = []
    for subject in subjects:
        subjects_list.append({
            "id": subject.id,
            "title": subject.title
        })
    return jsonify(subjects_list)

@subjects_bp.route("/subjects/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_task(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    t_list=[]
    for t in subject.tasks:
        t_list.append({
            "id": t.id,
            "task": t.task

        })
    return jsonify({
        "title": subject.title,
        "tasks": t_list
    })