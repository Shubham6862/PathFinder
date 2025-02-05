from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'pathfinder'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)

@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM users WHERE email=%s", [email])
        user = cur.fetchone()
        cur.close()

        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'danger')
            return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])

        preferences = {
            'historical_places': request.form.get('historical_places', 'no'),
            'museums': request.form.get('museums', 'no'),
            'modern_attractions': request.form.get('modern_attractions', 'no'),
            'nightlife': request.form.get('nightlife', 'no'),
            'nature': request.form.get('nature', 'no'),
            'adventure': request.form.get('adventure', 'no'),
            'relaxation': request.form.get('relaxation', 'no'),
            'wellness': request.form.get('wellness', 'no'),
            'local_experiences': request.form.get('local_experiences', 'no'),
            'cultural_events': request.form.get('cultural_events', 'no'),
        }

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        mysql.connection.commit()
        user_id = cur.lastrowid

        cur.execute("INSERT INTO user_preferences (user_id, " +
                    ", ".join(preferences.keys()) + ") VALUES (%s, " +
                    ", ".join(["%s"] * len(preferences)) + ")", 
                    [user_id] + list(preferences.values()))
        mysql.connection.commit()
        cur.close()

        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('home'))

    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        return "Welcome to the Dashboard"
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
