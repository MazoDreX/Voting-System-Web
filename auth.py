from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
import json
from werkzeug.security import generate_password_hash, check_password_hash
from voter_data import VotersData
from candidate_data import CandidateData
from paillier import PaillierEVoting
import logging

logging.basicConfig(level=logging.DEBUG)

# Blueprint untuk auth
auth = Blueprint('auth', __name__)

e_voting = PaillierEVoting()

# Dummy user database dengan role
users = {
    "admin": {"password": "admin123", "role": "admin"}
}

voting_status = {"status": "inactive"}

candidates = CandidateData()
def create_candidate_map(candidates_data):
    return {candidate['name']: idx + 1 for idx, candidate in enumerate(candidates_data)}
candidates_name = candidates.load_candidates()
candidate_map = create_candidate_map(candidates_name)
print(f"Candidate Name: {candidates_name}")
print(f"Candidate Map: {candidate_map}")


voters_data = VotersData()
@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        voter_id = request.form["id"]  # Menggunakan id untuk login
        password = request.form["password"]
        

        # Pertama, cek apakah ID terdapat dalam data dummy
        if voter_id in users:
            user = users[voter_id]

            # Periksa apakah password cocok
            if user["password"] == password:
                # Simpan id dan role dalam session
                session["id"] = voter_id
                session["role"] = user["role"]
                
                flash("Login successful!", "success")

                # Redirect sesuai dengan role
                if session["role"] == "admin":
                    return redirect(url_for("auth.admin_dashboard"))
                else:
                    return redirect(url_for("auth.user_dashboard"))
            else:
                flash("Invalid password.", "danger")
        else:
            # Jika ID tidak ada di data dummy, lanjutkan pengecekan di voters_data
            voters = voters_data.load_voters()
            print(voters)
            # Mencari voter berdasarkan ID
            voter = next((v for v in voters if v["id"] == voter_id), None)

            if voter:
                # Periksa apakah password cocok
                if "password" not in voter or voter["password"] is None:
                    flash("Belum ada password! Silahkan registrasi terlebih dahulu.", "danger")
                    return render_template("login.html")  # Arahkan ke halaman registrasi

                if check_password_hash(voter["password"],password):
                    # Simpan id dan role dalam session
                    session["id"] = voter_id
                    session["role"] = voter.get("role", "user")  # Default role adalah "user" jika tidak ada

                    flash("Login successful!", "success")

                    # Redirect sesuai dengan role
                    if session["role"] == "admin":
                        return redirect(url_for("auth.admin_dashboard"))
                    else:
                        return redirect(url_for("auth.user_dashboard"))
                else:
                    flash("Invalid password.", "danger")
            else:
                flash("Voter ID tidak ditemukan.", "danger")
    
    return render_template("login.html")

@auth.route("/admin")
def admin_dashboard():
    if "id" in session and session.get("role") == "admin":
        return render_template("admin.html", id=session["id"])
    else:
        flash("Akses ditolak. Admins only.", "danger")
        return redirect(url_for("auth.login"))

@auth.route("/user")
def user_dashboard():
    if "id" in session and session.get("role") == "user":
        print(voting_status)
        return render_template("user.html", id=session["id"])
    else:
        flash("Akses ditolak. Users only.", "danger")
        return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    session.pop("id", None)
    session.pop("role", None)
    flash("Anda logged out.", "info")
    return redirect(url_for("auth.login"))

@auth.route("/api/check_user/<string:voter_id>", methods=["GET"])
def check_user(voter_id):
    # Cari voter berdasarkan ID
    voters = voters_data.load_voters()
    for voter in voters:
        print("WAAAAAAAAAAAAAAAAAAAAAAA",voter)
        if voter["id"] == voter_id:
            return jsonify({"exists": True}), 200
    return jsonify({"exists": False}), 404

@auth.route("/api/register", methods=["POST"])
def register():
    data = request.json
    voter_id = data.get("voterId")
    password = data.get("Password")
    
    if not voter_id or not password:
        return jsonify({"message": "UserId and password are required"}), 400
    
    # Cek apakah voter sudah terdaftar
    voters = voters_data.load_voters()
    voter = next((v for v in voters if v["id"] == voter_id), None)
    
    if not voter:
        return jsonify({"message": "Voter ID not found"}), 404
    
    # Hash password sebelum disimpan (gunakan secure hashing)
    hashed_password = generate_password_hash(password)

    # Simpan password yang telah di-hash ke dalam data voter
    voter["password"] = hashed_password

    # Simpan data kembali ke file
    voters_data.save_voters(voters)

    return jsonify({"success": True, "message": "Registration successful"}), 201

@auth.route("/admin/start_voting", methods=["POST"])
def start_voting():
    """
    Admin memulai voting.
    """
    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    voting_status["status"] = "active"
    return jsonify({"message": "Voting telah dimulai."}), 200

@auth.route("/admin/end_voting", methods=["POST"])
def end_voting():
    """
    Admin menyelesaikan voting.
    """
    if voting_status["status"] != "active":
        return jsonify({"error": "Voting tidak sedang aktif."}), 400

    if session.get("role") != "admin":
        return jsonify({"error": "Unauthorized"}), 403

    voting_status["status"] = "completed"
    return jsonify({"message": "Voting telah selesai."}), 200

@auth.route("/voting_status", methods=["GET"])
def get_voting_status():
    """
    Cek status voting.
    """
    return jsonify(voting_status), 200

@auth.route("/api/vote", methods=["POST"])
def vote():
    """
    User memberikan suara.
    """
    if voting_status["status"] != "active":
        return jsonify({"error": "Voting belum dimulai atau sudah selesai."}), 400

    # Proses vote (contoh sederhana)
    data = request.get_json()
    logging.debug(f"Data diterima: {data}")
    voter_id = data.get("voterId")
    choice = data.get("candidate")

    if not choice:
        return jsonify({"error": "Pilihan kandidat diperlukan."}), 400
    
    try:
        # Lakukan enkripsi
        encrypted_vote = e_voting.vote(voter_id, choice, candidate_map)
        logging.debug(f"Voter {voter_id} memilih {choice}")
        logging.debug(f"ENKRIPSI: {encrypted_vote}")
        # Suara berhasil disimpan
        return jsonify({"message": "Vote berhasil disimpan.", "encrypted_vote": encrypted_vote.ciphertext()}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@auth.route("/api/results", methods=["GET"])
def results():
    """
    Menampilkan hasil voting setelah voting selesai.
    """
    if voting_status["status"] != "completed":
        return jsonify({"error": "Hasil hanya dapat ditampilkan setelah voting selesai."}), 400

    try:
        # Dekripsi dan hitung hasil suara
        results = e_voting.tally_votes(candidates_name, candidate_map)
        print(results)

        return jsonify({"results": results, "candidates": candidates_name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
