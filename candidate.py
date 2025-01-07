from flask import Blueprint, jsonify, request, session
from candidate_data import CandidateData

candidate_bp = Blueprint("candidate", __name__, url_prefix="/api/candidates")
candidate_data = CandidateData()

# Get all candidates (Admin only)
@candidate_bp.route("/", methods=["GET"])
def get_candidates():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    candidates = candidate_data.load_candidates()
    return jsonify({"candidates": candidates})

# Add a new candidate (Admin only)
@candidate_bp.route("/", methods=["POST"])
def add_candidate():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    data = request.json
    candidates = candidate_data.load_candidates()
    candidates.append(data["name"])
    candidate_data.save_candidates(candidates)
    return jsonify({"message": f"Kandidat {data['name']} ditambahkan!"}), 201

# Delete a candidate (Admin only)
@candidate_bp.route("/<int:index>", methods=["DELETE"])
def delete_candidate(index):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    candidates = candidate_data.load_candidates()
    if index < len(candidates):
        deleted = candidates.pop(index)
        candidate_data.save_candidates(candidates)
        return jsonify({"message": f"Kandidat {deleted} dihapus!"}), 200
    return jsonify({"error": "Index tidak valid"}), 404
