from flask import Flask, Blueprint, jsonify

ping_bp = Blueprint("ping", __name__, url_prefix="/api/ping")

@ping_bp.route("/ping", methods=['GET'])
def ping():
    return jsonify({"message": "Flask app is running successfully!"}), 200
