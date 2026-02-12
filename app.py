import os
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from dotenv import load_dotenv

# Завантажуємо .env
load_dotenv()

from errors.content_review_error import ContentNeedsReviewError
from models import db
from auth.auth import auth_bp
from tasks_endpoints import tasks_bp
from subject_endpoints import subjects_bp
from answer_endpoints import answers_bp
from users_endpoints import users_bp
from uploads_endpoints import uploads_bp
from moderate_generate_endpoints import ai_bp
from config import Config

# Створюємо Flask
app = Flask(__name__)

# --- Конфігурація через змінні середовища ---
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "default-secret-key")
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "default-jwt-secret")
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI", "sqlite:///school.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = os.getenv("SQLALCHEMY_TRACK_MODIFICATIONS", "False") == "True"
app.config["UPLOADS"] = os.getenv("UPLOADS", "./uploads")
app.config["ALLOWED_EXTENSIONS"] = {"png", "jpg", "jpeg", "gif"}  # приклад

# --- CORS ---
CORS(app)

# --- Error handler ---
@app.errorhandler(ContentNeedsReviewError)
def handle_review_error(e: ContentNeedsReviewError):
    return jsonify({
        "msg": e.message,
        "code": e.code
    }), 400

# --- DB та JWT ---
db.init_app(app)
jwt = JWTManager(app)
from flask import send_from_directory

# --- Blueprints ---
app.register_blueprint(uploads_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(tasks_bp)
app.register_blueprint(subjects_bp)
app.register_blueprint(answers_bp)
app.register_blueprint(users_bp)
app.register_blueprint(ai_bp)

# --- Тестовий ендпоінт ---
@app.route("/")
def home():
    return "health"

# --- Створення бази при запуску ---
def create_database():
    db_path = app.config["SQLALCHEMY_DATABASE_URI"].replace("sqlite:///", "")
    if not os.path.exists(db_path):
        with app.app_context():
            db.create_all()
            print("Таблиці створені!")

# --- Функція для перевірки файлів ---
def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in app.config["ALLOWED_EXTENSIONS"]

# --- Запуск ---
if __name__ == "__main__":
    create_database()
    app.run(host="0.0.0.0", port=5000)


