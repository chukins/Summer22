from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import sqlite3


app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        email = request.form.get('email')
        print(username, password, email)
        if len(password) <= 7:
            return render_template("error.html", error="Password must be at least 8 characters long")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('''
            INSERT INTO LoginDetails (Username, Password, Email)
            VALUES (?, ?, ?)
            ''', (username, hashed, email))
        conn.commit()
        conn.close()
        #return redirect(url_for("login"))
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        if len(password) <= 7:
            return render_template("error.html", error="Password must be at least 8 characters long")
        hashed = hashlib.sha256(password.encode()).hexdigest()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM LoginDetails WHERE Username = ?", (username,hashed))
    return render_template("login.html")
    
@app.route("/welcome")
def welcome():
    return render_template("welcome.html", username=session['username'])

if __name__ == "__main__":
    app.run(debug=True)