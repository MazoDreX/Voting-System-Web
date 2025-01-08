from flask import Blueprint, render_template, request, redirect, url_for, flash, session

# Blueprint untuk auth
auth = Blueprint('auth', __name__)

# Dummy user database dengan role
users = {
    "admin": {"password": "admin123", "role": "admin"},
    "user1": {"password": "password123", "role": "user"},
    "user2": {"password": "mypassword", "role": "user"}
}

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]


        if username in users and users[username]["password"] == password:
            session["username"] = username
            session["role"] = users[username]["role"]  
            flash("Login successful!", "success")

            
            if users[username]["role"] == "admin":
                return redirect(url_for("auth.admin_dashboard"))
            else:
                return redirect(url_for("auth.user_dashboard"))
        else:
            flash("Invalid username or password.", "danger")

    return render_template("login.html")

@auth.route("/admin")
def admin_dashboard():
    
    if "username" in session and session.get("role") == "admin":
        return render_template("admin.html", username=session["username"])
    else:
        flash("Akses ditolak. Admins only.", "danger")
        return redirect(url_for("auth.login"))

@auth.route("/user")
def user_dashboard():
    
    if "username" in session and session.get("role") == "user":
        return render_template("user.html", username=session["username"])
    else:
        flash("Akses ditolak. Users only.", "danger")
        return redirect(url_for("auth.login"))

@auth.route("/logout")
def logout():
    session.pop("username", None)
    session.pop("role", None)
    flash("Anda logged out.", "info")
    return redirect(url_for("auth.login"))
