from flask import Flask, render_template, request, redirect, url_for, session
import hashlib
import sqlite3
import string
from flask_session import Session

acceptedChars = [x for x in string.punctuation+string.ascii_letters+string.digits]

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/")
def index():
    return render_template("index.html", username=session.get('username'))

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
        hashed = hashlib.sha512(password.encode()).hexdigest()
        c.execute('''
            INSERT INTO LoginDetails (Username, Password, Email)
            VALUES (?, ?, ?)
            ''', (username, hashed, email))
        conn.commit()
        conn.close()
        session["username"] = request.form.get("username")
        return render_template("welcome.html", username=session.get('username'))
    return render_template("register.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        #encodes password to check it against the database
        hashed = hashlib.sha512(password.encode()).hexdigest()
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        #checks that the username and password are in the database and match each other
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
    return render_template("welcome.html", username=session.get('username'))

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('About.html', username=session.get('username'))

@app.route('/Booking')
def Booking():
    bookDB = sqlite3.connect('database2.db')
    c = bookDB.cursor()
    return render_template('Bookings.html', username=session.get('username'))

@app.route('/DelBooking', methods=['POST', 'GET'])
def DelBooking():

    bookDB = sqlite3.connect('database2.db')
    c = bookDB.cursor()
    bookCheck = c.execute('''SELECT * FROM BookingInfo WHERE username = ?''', (session['username'],)).fetchone()
    if bookCheck is None:
        return render_template('DelBooking.html', book="No bookings found")
    bookDB.commit()

    if request.method == 'POST':
        booking = request.form.get('booking')
        Bookingconfirm = request.form.get('item')
        Bookingconfirm = Bookingconfirm.split(" ")
        Bookingconfirm[-1] = Bookingconfirm[-1].replace(")", "")
        Bookingconfirm[-1] = Bookingconfirm[-1].replace("'", "")
        c.execute('''DELETE FROM BookingInfo WHERE Username = ? AND BookingDate = ? AND Subject = ?''', (session['username'], booking, Bookingconfirm[-1]))
        bookDB.commit()
        bookDB.close()
        return render_template('index.html', username=session.get('username'))
    c = bookDB.cursor()
    bookCheck = c.execute('''SELECT * FROM BookingInfo WHERE username = ?''', (session['username'],)).fetchall()
    return render_template('DelBooking.html', username=session.get('username'), data=bookCheck)




@app.route('/cBooking', methods=['POST', 'GET'])
def cBooking():
    bookDB = sqlite3.connect('database2.db')
    if request.method == "POST":
        subject = request.form.get('subject')
        date = request.form.get('date')
        c = bookDB.cursor()
        bookCheck = c.execute('''INSERT INTO BookingInfo (Username, BookingDate, Subject) VALUES (?, ?, ?)''', (session['username'], date, subject))
        bookDB.commit()
        bookDB.close()
        return render_template("index.html", username=session.get('username'))
    c = bookDB.cursor()
    bookCheck = c.execute('''SELECT * FROM BookingInfo WHERE Username = ?''', (session['username'],)).fetchall()
    count = len(bookCheck)
    return render_template('CreateBooking.html', username=session.get('username'), count=count, book="You have reached the maximum amount of bookings")

@app.route('/eBooking', methods=['POST', 'GET'])
def eBooking():
    bookDB = sqlite3.connect('database2.db')
    if request.method == 'POST':
        Bookingconfirm = request.form.get('item')
        Bookingconfirm = Bookingconfirm.split(" ")
        Bookingconfirm[-1] = Bookingconfirm[-1].replace(")", "")
        Bookingconfirm[-1] = Bookingconfirm[-1].replace("'", "")

        NewBookingDate = request.form.get('NewDate')
        c = bookDB.cursor()
        bookCheck = c.execute('''SELECT * FROM BookingInfo WHERE Username = ?''', (session['username'],)).fetchall()
        if bookCheck is None:
            return render_template('EditBooking.html', username=session.get('username'), book="No bookings found")
        else:
            c.execute('''UPDATE BookingInfo
                       SET BookingDate = ? WHERE Subject = ?''',(NewBookingDate, Bookingconfirm[-1]))
            bookDB.commit()
            bookDB.close()
        return render_template('index.html', username=session.get('username'))
    c = bookDB.cursor()
    bookCheck = c.execute('''SELECT * FROM BookingInfo WHERE Username = ?''', (session['username'],)).fetchall()
    uniqueBookCheck = []
    for book in bookCheck:
        if book not in uniqueBookCheck:
            uniqueBookCheck.append(book)
    return render_template('EditBooking.html', username=session.get('username'), data=uniqueBookCheck)


if __name__ == "__main__":
    app.run(debug=True)
