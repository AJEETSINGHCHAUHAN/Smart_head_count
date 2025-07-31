from flask import Flask, render_template, request, redirect, session, Response
from flask_mysqldb import MySQL
import uuid, hashlib, cv2, os
from datetime import datetime
from utils import generate_otp, send_otp
from db_config import app, mysql
from ultralytics import YOLO

app.secret_key = 'your_secret_key_here'

print("📂 Current working directory:", os.getcwd())

absolute_model_path = os.path.abspath('runs/train/people_counting/weights/best.pt')
model = None
print("🔍 Checking for YOLO model at:", absolute_model_path)

if os.path.exists(absolute_model_path):
    print("✅ YOLO model found!")
    model = YOLO(absolute_model_path)
else:
    print("❌ YOLO model not found. Please train it using train_yolo.py first.")

# Global State
camera = None
counting_active = False
last_person_count = 0

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/')
def home():
    return redirect('/login')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        hashed_password = hash_password(password)
        otp = generate_otp()

        session['otp'] = otp
        session['temp_user'] = {
            'username': username,
            'email': email,
            'password': hashed_password
        }

        if send_otp(email, otp):
            return redirect('/verify_otp')
        else:
            return "❌ Failed to send OTP."
    return render_template('signup.html')

@app.route('/verify_otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        if request.form['otp'] == session.get('otp'):
            user = session.get('temp_user')
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)",
                           (user['email'], user['username'], user['password']))
            mysql.connection.commit()
            cursor.close()
            session.pop('otp')
            session.pop('temp_user')
            return redirect('/login')
        else:
            return "❌ Invalid OTP"
    return render_template('verify_otp.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE email=%s AND password=%s", (email, password))
        user = cursor.fetchone()
        cursor.close()

        if user:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['email'] = user[2]
            session['session_id'] = str(uuid.uuid4())
            return redirect('/welcome')
        else:
            return "❌ Invalid credentials."
    return render_template('login.html')

@app.route('/welcome')
def welcome():
    if 'user_id' in session:
        username = session['username']
        email = session['email']
        cursor = mysql.connection.cursor()
        cursor.execute(
            "SELECT count, timestamp FROM counts WHERE user_email = %s ORDER BY timestamp DESC LIMIT 1",
            (email,)
        )
        result = cursor.fetchone()
        cursor.close()
        last_count = result[0] if result else None
        last_timestamp = result[1].strftime('%Y-%m-%d %H:%M:%S') if result else None

        return render_template('welcome.html', username=username,
                               last_count=last_count, last_timestamp=last_timestamp)
    return redirect('/login')

@app.route('/counting')
def counting():
    global counting_active
    if not model:
        return "❌ YOLO model not loaded. Please train it first."
    if 'user_id' in session:
        counting_active = True
        return render_template('counting.html')
    return redirect('/login')

@app.route('/stop')
def stop():
    global counting_active, last_person_count
    counting_active = False
    session['last_count'] = last_person_count
    session['last_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return redirect('/save_prompt')

def gen_frames():
    global camera, counting_active, last_person_count
    camera = cv2.VideoCapture(0)

    while counting_active and camera.isOpened():
        success, frame = camera.read()
        if not success:
            break

        results = model(frame, stream=True)
        person_count = 0
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    person_count += 1

        last_person_count = person_count
        cv2.putText(frame, f'People Count: {person_count}', (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        _, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    camera.release()
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    if not model:
        return "❌ Model not loaded"
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/save_prompt')
def save_prompt():
    count = session.get('last_count', 0)
    timestamp = session.get('last_timestamp', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    return render_template('save_prompt.html', count=count, timestamp=timestamp)

@app.route('/save_count', methods=['POST'])
def save_count():
    if 'user_id' in session:
        count = request.form.get('count')
        timestamp = request.form.get('timestamp')
        try:
            cursor = mysql.connection.cursor()
            cursor.execute("INSERT INTO counts (user_email, count, timestamp) VALUES (%s, %s, %s)",
                           (session['email'], count, timestamp))
            mysql.connection.commit()
            cursor.close()
            return redirect('/welcome')
        except Exception as e:
            print(f"[DB ERROR] {e}")
            return "❌ Failed to save count."
    return redirect('/login')

@app.route('/start_counting')
def start_counting():
    return redirect('/counting')

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return redirect('/login')

@app.route('/test_db')
def test_db():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT DATABASE();")
        db = cursor.fetchone()
        return f"✅ Connected to database: {db[0]}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    app.run(debug=True)
