from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import join_room, leave_room, send, SocketIO
from pymongo import MongoClient

import random
from string import ascii_uppercase

app = Flask(__name__)
app.config["SECRET_KEY"] = "hjhjsdahhds"
socketio = SocketIO(app)

rooms = {}

def generate_unique_code(length):
    while True:
        code = ""
        for _ in range(length):
            code += random.choice(ascii_uppercase)
        
        if code not in rooms:
            break
    
    return code

client = MongoClient("mongodb://localhost:27017/")
db = client["signup_db"]
collection = db["users"]

import re  # Import the regular expression module

import re  # Import the regular expression module

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['e']  # Access the 'e' field for email
        username = request.form['u']  # Access the 'u' field for username
        password = request.form['p']  # Access the 'p' field for password
        preferred_subjects = request.form['preferred_subjects']  # New field for preferred subjects
        about_me = request.form['about_me']  # New field for about me
        education = request.form['education']  # New field for education

        # Check the password length and email format
        if len(password) < 8 or not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            return render_template('signup.html', error="Password must be at least 8 characters long or check the email format")

        # Check if the email and username already exist in the database
        existing_user = collection.find_one({'email': email})
        existing_user_username = collection.find_one({'username': username})
        if existing_user:
            return render_template('signup.html', error="Email already exists")
        if existing_user_username:
            return render_template('signup.html', error="Username already exists")

        # If both checks pass and the email is not found in the database, insert the data into the database
        data = {
            'email': email,
            'username': username,
            'password': password,
            'preferred_subjects': preferred_subjects,
            'about_me': about_me,
            'education': education
        }
        collection.insert_one(data)
        return redirect(url_for('front'))

    return render_template('signup.html')

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check if user exists in the database
        user = collection.find_one({"email": email, "password": password})

        if user:
            return redirect(url_for('front'))
        else:
            return redirect(url_for('dashboard'))

    return render_template("login.html")






@app.route("/")
def dashboard():
    return render_template("frontpage.html")

@app.route("/home", methods=["POST", "GET"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join", False)
        create = request.form.get("create", False)

        if not name:
            return render_template("home.html", error="Please enter a name.", code=code, name=name)

        if join != False and not code:
            return render_template("home.html", error="Please enter a room code.", code=code, name=name)
        
        room = code
        if create != False:
            room = generate_unique_code(4)
            rooms[room] = {"members": 0, "messages": []}
        elif code not in rooms:
            return render_template("home.html", error="Room does not exist.", code=code, name=name)
        
        session["room"] = room
        session["name"] = name
        return redirect(url_for("room"))

    return render_template("home.html")

@app.route("/room")
def room():
    room = session.get("room")
    if room is None or session.get("name") is None or room not in rooms:
        return redirect(url_for("home"))

    return render_template("room.html", code=room, messages=rooms[room]["messages"])

@app.route("/notes")
def notes():
    return render_template("Notes.html")

@app.route("/front")
def front():
    return render_template("index2.html")

@app.route("/premium")
def premium():
    return render_template("premimum_trial.html")

@app.route('/profile')
def profile():
    return render_template("profile.html")
    

@socketio.on("message")
def message(data):
    room = session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": session.get("name"),
        "message": data["data"]
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")
    

@socketio.on("connect")
def connect(auth):
    room = session.get("room")
    name = session.get("name")
    if not room or not name:
        return
    if room not in rooms:
        leave_room(room)
        return
    
    join_room(room)
    send({"name": name, "message": "has entered the room"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")

@socketio.on("disconnect")
def disconnect():
    room = session.get("room")
    name = session.get("name")
    leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    send({"name": name, "message": "has left the room"}, to=room)
    print(f"{name} has left the room {room}")

    

if __name__ == "__main__":
    socketio.run(app, debug=True, host='0.0.0.0', port=80)

