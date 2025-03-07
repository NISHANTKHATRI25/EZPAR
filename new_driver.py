from flask import Flask, render_template, redirect, request, session,g
import psycopg2

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def get_db():
    if 'db' not in g:
        g.db = psycopg2.connect(
            host="localhost",
            database="ezpar",
            user="postgres",
            password="9999247971"
        )
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.teardown_appcontext
def teardown_db(e=None):
    close_db()

@app.route('/')
def mover():
    return redirect('/login')

@app.route('/home')
def home():
    db = get_db()
    cur = db.cursor()

    cur.execute('SELECT club_name, image, club_id FROM clubs;')
    clubs = cur.fetchall()

    cur.execute('SELECT a.type_name, b.event_name, b.event_date FROM events b, event_type a WHERE b.event_type = a.type_id ORDER BY b.event_id DESC LIMIT 5')
    events = cur.fetchall()

    return render_template('home.html', club=clubs, u_type=session.get('utype', -1), events=events)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html', message='Please register')
    if request.method == 'POST':
        email = request.form['email']
        passwd = request.form['password']
        name = request.form['username']
        c_passwd = request.form['c_password']

        db = get_db()
        cur = db.cursor()
        cur.execute(f'SELECT passwd, u_type FROM user_info WHERE u_email = \'{email}\';')
        f_passwd = cur.fetchone()

        if passwd != c_passwd:
            return render_template('register.html', message="passwords don't match")

        if f_passwd is None:
            db.commit()
            cur.execute(f'INSERT INTO user_info(u_name, u_email, passwd) VALUES (\'{name}\', \'{email}\', \'{passwd}\');')
            db.commit()
            db.close()
            return render_template('login.html', message="Account created! Login to continue")
        else:
            return render_template('login.html', message="Account already exists! Login to continue")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html', message='Login to Continue')
    if request.method == 'POST':
        email = request.form['email']
        passwd = request.form['password']

        db = get_db()
        cur = db.cursor()
        cur.execute(f'SELECT passwd, u_type, u_id FROM user_info WHERE u_email = \'{email}\';', )
        info = cur.fetchone()
        cur.execute('SELECT club_name, image, club_id FROM clubs;')
        clubs = cur.fetchall()
        db.commit()
        db.close()

        if info is None:
            return render_template('login.html', message='No such account exists')

        if info[0] == passwd:
            session['uid'] = info[2]
            session['utype'] = info[1]
            return redirect('/home')
        else:
            return render_template('login.html', message='Wrong Password! Try again')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/club/<int:club_id>')
def club(club_id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT club_name, club_description, image FROM clubs WHERE club_id = %s;', (club_id,))
    club_info = cur.fetchone()
    db.close()

    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM events WHERE club_id = %s;', (club_id,))
    events = cur.fetchall()
    db.close()

    return render_template('club_page.html', club_info=club_info, events=events, u_type=session.get('utype', -1))

@app.route('/add_event')
def add_event():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT club_name FROM clubs;')
    club_names = cur.fetchall()
    cur.execute('SELECT * FROM event_type;')
    event_types = cur.fetchall()
    db.close()

    return render_template('add_event.html', clubs=club_names, types=event_types, u_type=session.get('utype', -1))

@app.route('/submit_event', methods=['GET', 'POST'])
def submit_event():
    if request.method == 'POST':
        eventName = request.form['eventName']
        eventImage = request.form['eventImage']
        eventDescription = request.form['eventDescription']
        eventDate = request.form['eventDate']
        clubSelection = request.form['clubSelection']
        eventType = request.form['eventType']

        db = get_db()
        cur = db.cursor()
        cur.execute(f'SELECT type_id FROM event_type WHERE type_name=\'{eventType}\';')
        type_id = cur.fetchall()
        cur.execute(f'SELECT club_id FROM clubs WHERE club_name=\'{clubSelection}\';')
        club = cur.fetchall()
        cur.execute(f"INSERT INTO events (event_name, event_date, club_id, event_type, event_description, event_image) VALUES ('{eventName}', '{eventDate}', {club[0][0]}, {type_id[0][0]}, '{eventDescription}', '{eventImage}');")
        db.commit()
        db.close()

        return redirect('/home')

if __name__ == '__main__':
    app.run(debug=True)
