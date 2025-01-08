from flask import Flask,render_template, redirect, url_for, session, flash
from auth import auth
from candidate import candidate_bp
from candidate_data import CandidateData
from voter import voter_bp

app = Flask(__name__)
app.secret_key = "SECRET_KEY"

app.register_blueprint(auth)
app.register_blueprint(candidate_bp)
app.register_blueprint(voter_bp)

candidate_data = CandidateData()

@app.route("/")
def home():
    return redirect(url_for("auth.login"))

@app.route("/dashboard")
def dashboard():
    if "role" not in session:
        return redirect(url_for("auth.login"))
    if session["role"] == "admin":
        return render_template("admin.html")
    elif session["role"] == "user":
        candidates = candidate_data.load_candidates()
        return render_template("user.html", candidates=candidates)
    return "Role tidak dikenal!"

if __name__ == "__main__":
    app.run(debug=True)