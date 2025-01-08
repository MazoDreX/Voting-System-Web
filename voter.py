import os
import qrcode
from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
from voter_data import VotersData
from gen_key import KeyManager
import uuid

voters_data = VotersData()
key_manager = KeyManager()

voter_bp = Blueprint("voter", __name__, url_prefix="/api/voters")

QR_CODE_FOLDER = "static/qrcodes"
os.makedirs(QR_CODE_FOLDER, exist_ok=True)

# Get data (MODIFIKASI SUPAYA BISA DIGABUNGIN DENGAN QR CODE DAN STATUS VOTING)
@voter_bp.route("/", methods=["GET"])
def get_voters():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    voters = voters_data.load_voters()
    return jsonify({"voters": voters})

@voter_bp.route("/", methods=["POST"])
def add_voters():
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403
    
    print("Form Data: ", request.form)
    name=request.form.get("name")
    voter_id=request.form.get("id")
    tanggal_lahir=request.form.get("tanggalLahir")
    jenis_kelamin=request.form.get("jenisKelamin")
    alamat=request.form.get("alamat")
    
    if not all([name, voter_id, tanggal_lahir, jenis_kelamin, alamat]):
        return jsonify({"error": "Semua field wajib diisi!"}), 400
    
    # BUAT KUNCI
    private_key_path, public_key_path = key_manager.generate_keys(voter_id)
    

    # BUAT QR CODE
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(key_manager.get_public_key_pem(voter_id))
    qr.make(fit=True)
    
    qr_img_path = os.path.join(QR_CODE_FOLDER, f"{voter_id}.png")
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_img.save(qr_img_path)

    # MASUKAN DATA
    new_voter = {
        "name": name,
        "id": voter_id,
        "tanggalLahir": tanggal_lahir,
        "jenisKelamin": jenis_kelamin,
        "alamat": alamat,
        "public_key": public_key_path,
        "qr_code": qr_img_path,
    }

    voters = voters_data.load_voters()
    
    voters = []
    voters.append(new_voter)
    voters_data.save_voters(voters)

    return jsonify({"message": f"Voter {name} berhasil ditambahkan!", "qr_code": qr_img_path}), 201
    
