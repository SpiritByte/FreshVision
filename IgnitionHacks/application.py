import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    phone_num = db.Column(db.String, nullable=False)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
@login_required
def home():
    return render_template("index.html")
    
    
@app.route('/register', methods =["GET", "POST"])
def register():
    if request.method == "POST":
        username1 = request.form.get("name")
        password1 = request.form.get("password")
        phone_num1 = request.form.get("phone_num")
        confirm_password = request.form.get("cpassword")
        usernames = [user.username for user in User.query.all()]
        if username1 in usernames:
            return render_template("register.html", error="Username Taken")
        if password1 != confirm_password:
            return render_template("register.html", error="Passwords do not match")
        user = User(
            username = username1, password = password1, phone_num = phone_num1
        )
        db.session.add(user)
        db.session.commit()
        return redirect(url_for("login"))
    else:
        return render_template("register.html")
    
    
@app.route('/login', methods =["GET", "POST"])
def login():

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if not user:
            return render_template("login.html", error="User not found") 
        if user.password != password:
            return render_template("login.html", error="Password Invalid") 
        session["user_id"] = user.id
        return redirect(url_for("home"))
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug=True)  
