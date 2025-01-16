import os
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from candidate_data import CandidateData

candidate_bp = Blueprint("candidate", __name__, url_prefix="/api/candidates")
candidate_data = CandidateData()

UPLOAD_FOLDER = "static/uploads/candidates"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

# Ambil data kandidat
@candidate_bp.route("/", methods=["GET"])
def get_candidates():
    candidates = candidate_data.load_candidates()
    return jsonify({"candidates": candidates})

# Tambah data kandidat
@candidate_bp.route("/", methods=["POST"])
def add_candidate():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    name = request.form.get("name")
    if not name:
        return jsonify({"Error": "Nama Kandidat diperlukan"}), 400
    
    photo = request.files.get("photo")
    photo_filename = None

    if photo and allowed_file(photo.filename):
        photo_filename = secure_filename(photo.filename)
        photo_path = os.path.join(UPLOAD_FOLDER, photo_filename)
        photo.save(photo_path)
    else:
        if photo:
            return jsonify({"error": "Format file tidak didukung"}), 400

    candidates = candidate_data.load_candidates()
    candidates.append({"name": name, "photo": photo_filename})
    candidate_data.save_candidates(candidates)

    return jsonify({"message": f"Kandidat {name} ditambahkan!", "photo": photo_filename}), 201

# Hapus data kandidat
@candidate_bp.route("/<int:index>", methods=["DELETE"])
def delete_candidate(index):
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    candidates = candidate_data.load_candidates()
    if index < len(candidates):
        deleted_candidate = candidates.pop(index)
        candidate_data.save_candidates(candidates)

        if deleted_candidate.get("photo"):
            photo_path = os.path.join(UPLOAD_FOLDER, deleted_candidate["photo"])
            if os.path.exists(photo_path):
                os.remove(photo_path)

        return jsonify({"message": f"Kandidat {deleted_candidate['name']} dihapus!"}), 200

    return jsonify({"error": "Index tidak valid"}), 404
