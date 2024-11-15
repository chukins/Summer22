from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import sqlite3
import string
from flask_session import Session
import bcrypt
salt = bcrypt.gensalt()
acceptedChars = [x for x in string.punctuation+string.ascii_letters+string.digits]

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        password = request.form.get('password')
        email = request.form.get('email')
        username = request.form.get('username')
        ConfirmPass = request.form.get('password2')
        if len(password) <= 7 :
            return render_template("error.html", error="Password must be at least 8 characters long")
        if password != ConfirmPass:
            return render_template("error.html", error="Passwords do not match")
        for z in password:
            if z not in acceptedChars:
                return render_template("error.html", error="Password contains characters that are not allowed")
        if len(username) <= 6 or len(username) >= 13:
            return render_template("error.html", error="Username must be between 6 and 12 characters long")
        for z in username:
            if z not in acceptedChars:
                return render_template("error.html", error="Username contains characters that are not allowed")
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO LoginDetails (Username, Password, Email)
            VALUES (?, ?, ?)
            ''', (username, bcrypt.hashpw(password.encode("UTF-8"), salt), email))
        conn.commit()
        conn.close()
        session["username"] = request.form.get("username")
        return render_template("welcome.html", username=session['username'])
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        hashed = bcrypt.hashpw(password.encode("UTF-8"), salt)
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        logCheck = c.execute('''SELECT * FROM LoginDetails WHERE
                              Username = ? AND Password = ?''',(username, hashed)).fetchone()
        if logCheck is None:
            return render_template("error.html", error="Invalid username or password")
        conn.close()
        session["username"] = request.form.get("username")
        return render_template('index.html', username=session.get('username'))
    return render_template("login.html")
    
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", username=session['username'])

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('About.html')

@app.route('/Booking')
def Booking():
    return render_template('Bookings.html')

@app.route('/DelBooking')
def DelBooking():
    return render_template('DelBooking.html', username=session['username'])

@app.route('/createBooking')
def cBooking():
    return render_template('CreateBooking.html', username=session['username'])

@app.route('/editBooking')
def eBooking():
    return render_template('EditBooking.html', username=session['username'])


if __name__ == "__main__":
    app.run(debug=True)