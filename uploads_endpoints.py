import os
from flask import Blueprint, send_from_directory, jsonify

uploads_bp = Blueprint("uploads_bp", __name__)

UPLOAD_FOLDER = os.path.join(os.getcwd(), "uploads")


@uploads_bp.route("/uploads/<filename>", methods=["GET"])
def get_uploaded_file(filename):
    try:
        return send_from_directory(UPLOAD_FOLDER, filename)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404