from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import datetime
import os

app = Flask(__name__)
app.secret_key = 'your secret key'
app.debug = True
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['TEMPLATES_AUTO_RELOAD'] = True


@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        confirmPassword = request.form['confirmPassword']
        if password != confirmPassword:
            msg = 'Password does not match'
            return render_template('register.html', msg=msg)
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("INSERT INTO users (name, email,phone, password) VALUES (?, ?, ?, ?)", (name, email,phone, password))
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
            session['phone'] = data[3]
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
        #find id of the listing
        c.execute("SELECT id FROM listings WHERE title = ? AND description = ? AND price = ? AND category = ? AND user_id = ? AND date = ?", (title, description, price, category,session['id'],current_date))
        listing_id = c.fetchone()
        if 'file' not in request.files:
            return redirect(url_for('home'))
        file = request.files['file']
        filename = str(listing_id[0]) + '.jpg'
        file.save('static/uploads/' + filename)
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

@app.route('/editlisting/<int:id>', methods=['GET', 'POST'])
def editlisting(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM listings WHERE id = ?", (id,))
    listing = c.fetchone()
    if listing[1] != session['id']:
        return 'You cannot edit this listing'
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        
        c.execute("UPDATE listings SET title = ?, description = ?, price = ?, category = ? WHERE id = ?", (title, description, price, category, id))
        conn.commit()
        c.execute("SELECT id FROM listings WHERE title = ? AND description = ? AND price = ? AND category = ? AND user_id = ?", (title, description, price, category,session['id']))
        listing_id = c.fetchone()
        
        if 'file' not in request.files:
            return redirect(url_for('viewmylistings'))
        '''
        filename=str(listing_id[0]) + '.jpg'
        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'],filename )
        print(old_image_path)
        os.remove(old_image_path)
        '''
        file = request.files['file']
        filename = str(listing_id[0]) + '.jpg'
        new_image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(new_image_path)
        return redirect(url_for('viewmylistings'))
        
    return render_template('editlisting.html', listing=listing)

@app.route('/editrequest/<int:id>', methods=['GET', 'POST'])
def editrequest(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests WHERE id = ?", (id,))
    requestx = c.fetchone()
    if requestx[1] != session['id']:
        return 'You cannot edit this request'
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        price = request.form['price']
        category = request.form['category']
        c.execute("UPDATE requests SET title = ?, description = ?, price = ?, category = ? WHERE id = ?", (title, description, price, category, id))
        conn.commit()
        return redirect(url_for('viewmyrequests'))
    return render_template('editrequest.html', request=requestx)

@app.route('/deletelisting/<int:id>')
def deletelisting(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM listings WHERE id = ?", (id,))
    listing = c.fetchone()
    if listing[1] != session['id']:
        return 'You cannot delete this listing'
    c.execute("DELETE FROM listings WHERE id = ?", (id,))
    conn.commit()
    return redirect(url_for('viewmylistings'))

@app.route('/deleterequest/<int:id>')
def deleterequest(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests WHERE id = ?", (id,))
    requestx = c.fetchone()
    if requestx[1] != session['id']:
        return 'You cannot delete this request'
    c.execute("DELETE FROM requests WHERE id = ?", (id,))
    conn.commit()
    return redirect(url_for('viewmyrequests'))



@app.route('/myprofile')
def myprofile():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (session['id'],))
    user = c.fetchone()
    return render_template('myprofile.html', user=user)


@app.route('/otherprofile/<int:id>')
def otherprofile(id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE id = ?", (id,))
    user = c.fetchone()
    return render_template('otherprofile.html', user=user)
