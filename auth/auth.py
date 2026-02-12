from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError
from models import User, db
from flask_jwt_extended import jwt_required, get_jwt_identity

from .schemas import LoginSchema, RegisterSchema

login_schema = LoginSchema()
register_schema = RegisterSchema()

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    user_id = int(get_jwt_identity())
    return {"user_id": user_id}

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
       data = register_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"msg": "Неправильні дані", "errors": e.messages}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"msg": "Користувач вже зареєстрований"}), 400

    user = User(
        name=data["name"],
        email=data["email"]
    )
    user.set_password(data["password"])

    db.session.add(user)
    db.session.commit()
    access_token = create_access_token(identity=str(user.id))


    return jsonify({
        "msg": "User registered",
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name, 
            "email": user.email
        }}), 201

@auth_bp.route("/login", methods=["POST"])
def login():
    try:
        data = login_schema.load(request.get_json(silent=True) or {})
    except ValidationError as e:
        return jsonify({"msg": "Validation error", "errors": e.messages}), 400
    
    user = User.query.filter_by(email=data["email"]).first()

    if not user or not user.check_password(data["password"]):
        return jsonify({"msg": "Invalid credentials"}), 401

    access_token = create_access_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "user": {
            "id": user.id,
            "name": user.name,
            "email": user.email
        }
    })

