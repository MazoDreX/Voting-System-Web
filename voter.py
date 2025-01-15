import os
import qrcode
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.exceptions import InvalidSignature
from flask import Blueprint, jsonify, request, session
from voter_data import VotersData
from gen_key import KeyManager


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
    qr.add_data(key_manager.get_private_key_pem(voter_id))
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
        "private_key": private_key_path,
        "qr_code": qr_img_path,
    }

    voters = voters_data.load_voters()
    voters.append(new_voter)
    voters_data.save_voters(voters)

    return jsonify({"message": f"Voter {name} berhasil ditambahkan!", "qr_code": qr_img_path}), 201
    
@voter_bp.route("/validate-private-key", methods=["POST"])
def validate_private_key():
    try:
        data = request.get_json()
        voter_id = data.get("voter_id")
        if not voter_id:
            return jsonify({"error": "voter_id is required"}), 400
        
        # Load keys
        private_key, public_key = key_manager.load_keys(voter_id)
        test_message = b"Ini adalah Aplikasi Sistem Voting."
        signature = private_key.sign(
            test_message,
            ec.ECDSA(hashes.SHA256())
        )
        try:
            public_key.verify(
                signature,
                test_message,
                ec.ECDSA(hashes.SHA256())
            )
            return jsonify({"message": "The key pair is valid!"}), 200
        except InvalidSignature:
            return jsonify({"error": "The key pair is invalid!"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

