from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from errors.content_review_error import ContentNeedsReviewError
from models import db
import os
from flask_cors import CORS

from config import Config

# 1️⃣ Імпорт blueprint
from auth.auth import auth_bp  
from tasks_endpoints import tasks_bp  
from subject_endpoints import subjects_bp
from answer_endpoints import answers_bp
from users_endpoints import users_bp

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

@app.errorhandler(ContentNeedsReviewError)
def handle_review_error(e: ContentNeedsReviewError):
    return jsonify({
        "msg": e.message,
        "code": e.code
    }), 400

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///school.db'
# app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
jwt = JWTManager(app)

# 2️⃣ Реєстрація blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(answers_bp)
app.register_blueprint(users_bp)

@app.route("/")
def home():
    return "health"

def create_database():
    if not os.path.exists("school.db"):
        with app.app_context():
            db.create_all()
            print("Таблиці створені!")


if __name__ == "__main__":
    create_database()
    app.run()


