from flask import Flask, render_template, redirect,request
from datetime import date
import psycopg2

utype=-1
uid=-1

app = Flask(__name__)

@app.route('/')
def mover():
    return redirect('/login')

@app.route('/about_us')
def about_us():
    if utype==-1:
        return redirect('/login')
    return render_template('about_us.html',u_type=utype)

@app.route('/home')
def home():
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name,image,club_id FROM clubs;')
    clubs= cur.fetchall()
    cur.execute('Select a.type_name,b.event_name,b.event_date,b.event_id from events b,event_type a where b.event_type=a.type_id order by b.event_date desc limit 5')
    events=cur.fetchall()
    conn.commit()
    conn.close()
    return render_template('home.html',club=clubs,u_type=utype,events=events)


@app.route('/dashboard')
def dashboard():
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    today=date.today()
    cur.execute(f'select p.event_id,e.event_name,e.event_date from participants p,events e where p.user_id={uid} and p.event_id=e.event_id and e.event_date>\'{today}\';')
    upcoming_events=cur.fetchall();
    cur.execute(f'select p.event_id,e.event_name,e.event_date from participants p,events e where p.user_id={uid} and p.event_id=e.event_id and e.event_date<\'{today}\';')
    past_events=cur.fetchall();
    conn.close()
    
    return render_template('dashboard.html',upcoming=upcoming_events,past=past_events,u_type=utype)


@app.route('/register',methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html',message='Please register')
    if request.method == 'POST':
        email=request.form['email']
        passwd=request.form['password']
        name=request.form['username']
        c_passwd=request.form['c_password']

        conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
        cur = conn.cursor()
        cur.execute(f'SELECT passwd,u_type FROM user_info WHERE u_email = \'{email}\';')
        f_passwd=cur.fetchone()

        if passwd!=c_passwd:
            return render_template('register.html',message="passwords don't match")
        
        if f_passwd is None:
            conn.commit()
            cur.execute(f'Insert into user_info(u_name,u_email,passwd) values(\'{name}\',\'{email}\',\'{passwd}\'); ')
            conn.commit()
            conn.close()
            return render_template('login.html',message="Account created!Login to continue")
        else:
            return render_template('login.html',message="Account already exists!Login to continue")


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html',message='Login to Continue')
    if request.method == 'POST':
        email=request.form['email']
        passwd=request.form['password']

        conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
        cur = conn.cursor()
        cur.execute(f'SELECT passwd,u_type,u_id FROM user_info WHERE u_email = \'{email}\';', )
        info=cur.fetchone()
        cur.execute('SELECT club_name,image,club_id FROM clubs;')
        clubs= cur.fetchall()
        conn.commit()
        conn.close()

        if info is None:
            return render_template('login.html',message='No such account exists')

        if (info[0]==passwd):
            global utype,uid
            uid=info[2]
            utype=info[1]
            return redirect('/home')
        else:
            return render_template('login.html',message='Wrong Password ! try again')


@app.route('/club/<int:club_id>')
def club(club_id):
    if utype==-1:
        return redirect('/login')
    today=date.today()
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute(f'SELECT club_name, club_description,image FROM clubs WHERE club_id = {club_id};')
    club_info = cur.fetchone()

    cur.execute(f'SELECT event_id,event_name,event_date FROM events WHERE club_id = {club_id} and event_date>\'{today}\';')
    events = cur.fetchall()
    cur.execute(f'SELECT event_id,event_name,event_date FROM events WHERE club_id = {club_id} and event_date<\'{today}\';')
    past_events = cur.fetchall()
    conn.close()

    return render_template('club_page.html', club_info=club_info, events=events,u_type=utype,past_events=past_events)

@app.route('/add_event')
def add_event():
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name FROM clubs;')
    club_names = cur.fetchall()
    cur.execute('SELECT * FROM event_type;')
    event_types = cur.fetchall()
    conn.close()
    return render_template('add_event.html',clubs=club_names,types=event_types,u_type=utype)

@app.route('/submit_event',methods=['GET','POST'])
def submit_event():
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    cur.execute('SELECT club_name FROM clubs;')
    club_names = cur.fetchall()
    cur.execute('SELECT * FROM event_type;')
    event_types = cur.fetchall()
    
    if request.method == 'POST':
        eventName=request.form['eventName']
        eventImage=request.form['eventImage']
        eventDescription=request.form['eventDescription']
        eventDate=request.form['eventDate']
        clubSelection=request.form['clubSelection']
        eventType=request.form['eventType']

        if eventDate<=str(date.today()):
            message=" Please enter a date at least one day away from today !!"
            return render_template('add_event.html',clubs=club_names,types=event_types,u_type=utype,message=message)
        
        cur.execute(f'SELECT type_id FROM event_type where type_name=\'{eventType}\';')
        type_id = cur.fetchall()
        cur.execute(f'SELECT club_id FROM clubs where club_name=\'{clubSelection}\';')
        club=cur.fetchall()
        cur.execute(f"insert into events (event_name,event_date,club_id,event_type,event_description,event_image) values(\'{eventName}\',\'{eventDate}\',{club[0][0]},{type_id[0][0]},\'{eventDescription}\',\'{eventImage}\');")
        conn.commit()
        conn.close()
        return redirect('/home')

@app.route('/event/<int:event_id>')
def event(event_id):
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute(f"SELECT e.event_name,e.event_description,e.event_image,e.event_date,c.club_name,e.event_type,e.event_id FROM events e,clubs c where e.event_id={event_id} and c.club_id=e.club_id")
    event_data=cur.fetchone()
    today=date.today()
    event_status=-1
    event_result=''
    participated=0
    cur.execute(f'select * from participants where user_id={uid} and event_id={event_id};')
    par=cur.fetchone()
    if event_data[3]>today:
        event_status=1
        if par is None:
            return render_template('events.html',events=event_data,u_type=utype,event_status=event_status,result=event_result,participated=participated)
        else:
            participated=1
            return render_template('events.html',events=event_data,u_type=utype,event_status=event_status,result=event_result,participated=participated)            

    else:
        cur.execute(f'select event_result from results where event_id={event_id}')
        result=cur.fetchone()

        if result is None:
            event_status=2
            event_result='Result not added yet!!'
            return render_template('events.html',events=event_data,u_type=utype,event_status=event_status,result=event_result)

        else:
            event_status=3
            return render_template('events.html',events=event_data,u_type=utype,event_status=event_status,result=result[0])
            
    conn.close()
    
@app.route('/participate/<int:type_id>/<int:event_id>',methods=['POST','GET'])
def participate(type_id,event_id):
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
    host="localhost",
    database="ezpar",
    user="postgres",
    password="9999247971")
    cur = conn.cursor()
    if type_id==1:
        conn.close()
        return render_template('solo_event.html',event_id=event_id,u_type=utype,u_id=uid)
    elif type_id==2:
        cur.execute(f'select team_name from team_event where event_id={event_id};')
        team_names=cur.fetchall()
        no_teams=len(team_names)
        conn.close()
        return render_template('team_event.html',event_id=event_id,u_type=utype,u_id=uid,team_names=team_names,no_teams=no_teams)
            
    else:
        cur.execute(f'insert into participants values ({u_id},{event_id});')
        conn.commit()
        conn.close()
        return redirect('/dashboard')

@app.route('/load_event/<int:event_id>/<int:u_id>/<int:event_type>',methods=['GET','POST'])
def load_event(event_id,u_id,event_type):
    if utype==-1:
        return redirect('/login')
    
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()

    if event_type==1:
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        topic_name=request.form['topic_name']
        topic_description=request.form['topic_description']

        cur.execute(f'insert into solo_event values ({uid},\'{name}\',\'{email}\',\'{phone}\',\'{topic_name}\',\'{topic_description}\',{event_id});')
        conn.commit()
        cur.execute(f'insert into participants values ({u_id},{event_id});')
        conn.commit()

    if event_type==2:
        teamName=request.form['teamName']
        teamIdea=request.form['teamIdea']
        name=request.form['name']
        email=request.form['email']
        phone=request.form['phone']
        course=request.form['course']
        batch=request.form['batch']

        cur.execute(f'insert into team_event values ({uid},\'{name}\',\'{email}\',\'{phone}\',\'{course}\',\'{batch}\',\'{teamName}\',\'{teamIdea}\',{event_id});')
        conn.commit()
        cur.execute(f'insert into participants values ({u_id},{event_id});')
        conn.commit()

    if event_type==3:
        teamName=request.form['teamOptions']
        name=request.form['joinName']
        email=request.form['joinEmail']
        phone=request.form['joinPhone']
        course=request.form['joinCourse']
        batch=request.form['joinBatch']
        
        cur.execute(f'select team_idea from team_event where team_name=\'{teamName}\' and event_id={event_id}')
        teamIdea=cur.fetchone()
        cur.execute(f'insert into team_event values ({uid},\'{name}\',\'{email}\',\'{phone}\',\'{course}\',\'{batch}\',\'{teamName}\',\'{teamIdea[0]}\',{event_id});')
        conn.commit()
        cur.execute(f'insert into participants values ({u_id},{event_id});')
        conn.commit()
    conn.close()
    return redirect ('/dashboard')

@app.route('/profile')
def profile():
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    cur.execute(f'select u_name,u_email from user_info where u_id={uid};')
    u_data=cur.fetchone()
    conn.close()

    return render_template('profile.html',user_name=u_data[0],user_email=u_data[1],u_type=utype)

@app.route('/logout',methods=['GET','POST'])
def logout():
    global uid,utype
    if utype==-1:
        return redirect('/login')
    uid=-1
    utype=-1

    return redirect('/login')

@app.route('/add_result/<int:event_id>')
def add_result(event_id):
    if utype==-1:
        return redirect('/login')
    return render_template('add_result.html',event_id=event_id,u_type=utype)

@app.route('/load_result/<int:event_id>',methods=['GET','POST'])
def load_result(event_id):
    if utype==-1:
        return redirect('/login')
    conn = psycopg2.connect(
        host="localhost",
        database="ezpar",
        user="postgres",
        password="9999247971")
    cur = conn.cursor()
    result=request.form['result']
    cur.execute(f'insert into results values({event_id},\'{result}\');')
    conn.commit()
    return redirect('/home')
    

if __name__ == '__main__':
    app.run(debug=True)
