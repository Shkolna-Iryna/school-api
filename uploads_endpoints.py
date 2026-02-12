import os
from flask import Blueprint, send_from_directory, jsonify, current_app

uploads_bp = Blueprint("uploads_bp", __name__)

@uploads_bp.route("/uploads/<filename>")
def get_uploaded_file(filename):
    try:
        upload_folder = current_app.config["UPLOADS"]
        return send_from_directory(upload_folder, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404
