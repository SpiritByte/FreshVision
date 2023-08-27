import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from tempfile import mkdtemp
from functools import wraps
import requests
import tensorflow as tf
from PIL import Image
import numpy as np
import io



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
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    phone_num = db.Column(db.String, nullable=False)

class Recipes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fruit = db.Column(db.String, nullable=False)
    meal = db.Column(db.String, unique=True, nullable=False)
    ingridients = db.Column(db.String, nullable=False)

class Alerts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    alert = db.Column(db.String, nullable=False)
    person = db.Column(db.String, unique=True, nullable=False)

with app.app_context():
    db.create_all()

apple = [
    {
        "Apple Pie": [
            "Apples", "Sugar", "Cinnamon", "Pie crust",
            "Lemon juice", "Vanilla extract", "Butter", "Nutmeg", "Eggs"
        ]
    },
    {
        "Caramel Apples": [
            "Apples", "Caramel", "Nuts", "Chocolate"
        ]
    },
    {
        "Apple Cobbler": [
            "Apples", "Sugar", "Cinnamon", "Flour", "Baking powder",
            "Salt", "Milk", "Butter"
        ]
    },
    {
        "Fruit Salad (Apple)": [
            "Assorted fruits", "Honey", "Lime juice", "Mint leaves"
        ]
    },
    {
        "Fried Apples": [
            "Apples", "Sugar", "Cinnamon", "Butter"
        ]
    },
    {
        "Apple Tart": [
            "Apples", "Sugar", "Pie crust", "Apricot jam"
        ]
    },
    {
        "Apple Cider": [
            "Apples", "Water", "Sugar", "Cinnamon sticks", "Cloves"
        ]
    },
    {
        "Apple Juice": [
            "Apples", "Water", "Sugar", "Lemon juice"
        ]
    },
    {
        "Fruit Smoothie (Apple)": [
            "Assorted fruits", "Yogurt", "Honey", "Ice"
        ]
    }
]

# Orange-based Dishes
orange = [
    {
        "Orange Cake": [
            "Oranges", "Flour", "Sugar", "Butter", "Eggs",
            "Baking powder", "Vanilla extract", "Salt", "Milk"
        ]
    },
    {
        "Orange Bars": [
            "Oranges", "Flour", "Sugar", "Butter", "Eggs",
            "Vanilla extract", "Salt"
        ]
    },
    {
        "Orange Juice": [
            "Oranges", "Water", "Sugar", "Lemon juice"
        ]
    },
    {
        "Fruit Salad (Orange)": [
            "Assorted fruits", "Honey", "Lime juice", "Mint leaves"
        ]
    },
    # ...
    # Include other orange-based dishes
    # ...
]

# Banana-based Dishes
banana = [
    {
        "Banana Bread": [
            "Bananas", "Sugar", "Flour", "Butter", "Eggs",
            "Baking soda", "Salt", "Vanilla extract"
        ]
    },
    {
        "Banana Brownies": [
            "Bananas", "Sugar", "Butter", "Eggs", "Flour",
            "Cocoa powder", "Baking powder", "Salt"
        ]
    },
    {
        "Banana Muffins": [
            "Bananas", "Sugar", "Flour", "Butter", "Eggs",
            "Baking powder", "Salt", "Vanilla extract"
        ]
    },
    {
        "Banana Cookies": [
            "Bananas", "Sugar", "Butter", "Eggs", "Flour",
            "Baking soda", "Salt", "Vanilla extract", "Chocolate chips"
        ]
    },
    # ...
    # Include other banana-based dishes
    # ...
]
with app.app_context():
    for dish in apple:
        dish_name = next(iter(dish))
        ingredients = ','.join(dish[dish_name])
        recipe = Recipes(
            fruit='apple', meal=dish_name, ingridients=ingredients
        )
        if not Recipes.query.filter_by(fruit='apple', meal=dish_name).first():
            db.session.add(recipe)
            db.session.commit()

    for dish in orange:
        dish_name = next(iter(dish))
        ingredients = ','.join(dish[dish_name])
        recipe = Recipes (
            fruit='orange', meal=dish_name, ingridients=ingredients
        )
        if not Recipes.query.filter_by(fruit='orange', meal=dish_name).first():
            db.session.add(recipe)
            db.session.commit()


    for dish in banana:
        dish_name = next(iter(dish))
        ingredients = ','.join(dish[dish_name])
        recipe = Recipes (
            fruit='banana', meal=dish_name, ingridients=ingredients
        )
        if not Recipes.query.filter_by(fruit='banana', meal=dish_name).first():
            db.session.add(recipe)
            db.session.commit()


@app.route('/')
@login_required
def home():
    alerts = Alerts.query.filter_by(person=session["user_id"]).all()
    message = ""
    recipes = []
    for alert in alerts:
        message = alert.alert 
        recipes.append(recipe_suggest(message))
    return render_template("index.html", alerts=alerts, recipes=recipes)
    
    
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



model = tf.keras.models.load_model('model1.h5')


@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_photo():
    if request.method == 'POST':
        uploaded_file = request.files['image']
        if not uploaded_file:
            # Handle case where no image is uploaded
            return render_template('image.html', error="No image uploaded")
        uploaded_file = request.files['image']
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((240, 240))  # Resize to match model's input size
        image = np.array(image) / 255.0  # Normalize pixel values
        image = np.expand_dims(image, axis=0)  # Add batch dimension

        # Make predictions using the loaded model
        predictions = model.predict(image)
        fruits = ['apple', 'banana', 'orange']
        class_dict= {'Rotten Banana': 0, 'Orange': 1, 'Rotten Orange': 2, 'Banana': 3, 'Rotten Apple': 4, 'Apple': 5}
        rev_dict={}
        klass=""

        for key, value in class_dict.items():
            rev_dict[value]=key

        for i, p in enumerate(predictions):
            index=np.argmax(p)
            klass=rev_dict[index]    
            prob=p[index]

        if 'rotten' in klass.lower():
            for fruit in fruits:
                if fruit in predictions.lower():
                    alert = Alerts (
                        alert=predictions, person=session["user_id"]
                    )
                    with app.app_context():
                        db.session.add(alert)
                        db.session.commit()
        return redirect(url_for("home"))
    else:
        return render_template("image.html")

def recipe_suggest(fruit_type):
    with app.app_context():
        recipes = Recipes.query.filter_by(fruit=fruit_type).all()
        if len(recipes) > 3:
            recipes = recipes[:3]
    return recipes 

def send_message(phone_num, message):
    resp = requests.post('https://textbelt.com/text', {
        'phone': phone_num,
        'message': message,
        'key': 'textbelt', })
    print(resp.json())

@app.route('/about')
@login_required
def about():
    return render_template("about.html")

@app.route('/contact')
@login_required
def contact():
    return render_template("contact.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")
    
if __name__ == '__main__':
    app.run(debug=True)  