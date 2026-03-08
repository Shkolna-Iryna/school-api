from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from moderation import moderate_text
from dotenv import load_dotenv
from openai import OpenAI
import os
from models import Task, db
import json
import uuid


load_dotenv()  
ai_bp = Blueprint("ai", __name__)
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@ai_bp.route("/ai/moderation", methods=["POST"])
@jwt_required()
def moderate_text_api():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({"error": "Текст порожній"}), 400

    try:
        flagged = moderate_text(text)
        return jsonify({"flagged": flagged})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



active_tests = {}
@ai_bp.route("/generate/<int:task_id>", methods=["GET"])
@jwt_required()
def generate_test(task_id):

    task = db.session.get(Task, task_id)

    if not task:
        return jsonify({"message": "Task not found"}), 404

    prompt = f"""
    На основі цього питання:

    {task.task}

    Згенеруй 5 тестових питань.

    Поверни СТРОГО JSON у форматі:

    {{
      "tests": [
        {{
          "task": "Питання",
          "options": ["A", "B", "C", "D"],
          "correct_index": 0
        }}
      ]
    }}

    correct_index — це номер правильної відповіді (0,1,2 або 3).
    """

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Ти генератор тестів. Повертаєш тільки JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result = json.loads(response.choices[0].message.content)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

   
    test_id = str(uuid.uuid4())

    
    active_tests[test_id] = [
        t["correct_index"] for t in result["tests"]
    ]

    for t in result["tests"]:
        t.pop("correct_index", None)

    return jsonify({
        "test_id": test_id,
        "tests": result["tests"]
    })

@ai_bp.route("/check/<string:test_id>", methods=["POST"])
@jwt_required()
def check_test(test_id):

    if test_id not in active_tests:
        return jsonify({"message": "Test not found"}), 404

    data = request.get_json()
    user_answers = data.get("answers", [])

    correct_indexes = active_tests[test_id]

    score = sum(
        1 for i in range(len(correct_indexes))
        if i < len(user_answers) and user_answers[i] == correct_indexes[i]
    )

    return jsonify({
        "score": score,
        "total": len(correct_indexes),
        "correct_indexes": correct_indexes
    })
