from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = 'your secret key'
app.debug = True



@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        if password != confirmPassword:
            msg = 'Password does not match'
            return render_template('register.html', msg=msg)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, password))
        conn.commit()
        return redirect(url_for('login'))
    return render_template('register.html', msg='')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        
        email = request.form['email']
        password = request.form['password']        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
        data = c.fetchone()
        if data:
            session['name'] = data[1]
            session['email'] = data[2]
            session['id'] = data[0]
            return redirect(url_for('home'))
        return 'Invalid username or password'
    return render_template('login.html',msg='')

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('welcome'))

@app.route('/createlisting', methods=['GET', 'POST'])
def createlisting():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO listings (title, description, price, category,user_id,date) VALUES (?, ?, ?, ?, ?,?)", (title, description, price, category,session['id'],current_date))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('createlisting.html')

@app.route('/createrequest', methods=['GET', 'POST'])
def createrequest():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO requests (title, description, price, category,user_id,date) VALUES (?, ?, ?, ?, ?,?)", (title, description, price, category,session['id'],current_date))
        conn.commit()
        return redirect(url_for('home'))
    return render_template('createrequest.html')

@app.route('/viewlistings')
def viewlistings():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM listings where user_id != ?",(session['id'],))
    listings = c.fetchall()
    return render_template('viewlistings.html', listings=listings)

@app.route('/viewrequests')
def viewrequests():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests where user_id != ?",(session['id'],))
    requests = c.fetchall()
    return render_template('viewrequests.html', requests=requests)

@app.route('/viewmylistings')
def viewmylistings():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM listings where user_id = ?",(session['id'],))
    listings = c.fetchall()
    return render_template('viewmylistings.html', listings=listings)

@app.route('/viewmyrequests')
def viewmyrequests():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests where user_id = ?",(session['id'],))
    requests = c.fetchall()
    return render_template('viewmyrequests.html', requests=requests)


