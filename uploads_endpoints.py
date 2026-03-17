import os
from flask import Blueprint, send_from_directory, jsonify, current_app
from flask_jwt_extended import jwt_required

uploads_bp = Blueprint("uploads_bp", __name__)

@uploads_bp.route("/uploads/<filename>")
@jwt_required()
def get_uploaded_file(filename):
    try:
        upload_folder = current_app.config["UPLOADS"]
        return send_from_directory(upload_folder, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
import os
from flask import Blueprint, send_from_directory, current_app, jsonify

