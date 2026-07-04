import os, secrets, datetime, requests, time
from flask import Flask, render_template_string, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

app = Flask(__name__)
app.config.update(SECRET_KEY=secrets.token_hex(16), SQLALCHEMY_DATABASE_URI='sqlite:///saas.db', SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)
lm = LoginManager(app)
lm.login_view = 'login'

# HARDCODED LIVE VALUES
stripe.api_key = "sk_test_51Tke3WRsVgVw9kTXB7nWOrvb1jGUnCuTAqwgcX5OA7r7hxVh534pcyg5Y0D989GwT4CQmwsfN9SezJyb8gEdjXDF00OEi2JoDS"
AI_ENGINE_URL = "https://onrender.com"

CSS = "body{font-family:sans-serif;background:#0f172a;color:#fff;max-width:600px;margin:40px auto;padding:10px}.card{background:#1e293b;padding:20px;border-radius:8px;margin-bottom:15px}input,textarea{width:100%;padding:10px;margin:8px 0;background:#0f172a;color:#fff;border:1px solid #475569;border-radius:6px;box-sizing:border-box}button{width:100%;padding:12px;background:#38bdf8;border:none;color:#0f172a;font-weight:bold;border-radius:6px;cursor:pointer}pre{background:#020617;padding:15px;color:#34d399;overflow-x:auto;border-radius:6px}"

INDEX_HTML = f"""<!DOCTYPE html><html><head><style>{CSS}</style><title>AI Studio</title></head><body><div class='card'><a href='/logout' style='color:#94a3b8;float:right;'>Logout</a><h2>AI Dashboard Pro 🚀</h2><p>Account Profile: <b>{{{{current_user.username}}}}</b> | Balance: <span style='color:#38bdf8'>{{% if current_user.is_premium %}}👑 Premium Access{{% else %}}{{{{current_user.tokens}}}} / 15 Available{{% endif %}}</span></p>{{% if not current_user.is_premium and current_user.tokens <= 0 %}}<div style='background:#7c3aed;padding:10px;border-radius:6px;text-align:center;'>Tokens exhausted. 25h lock active. Upgrade via Stripe.</div>{{% endif %}}</div><div class='card'><textarea id='p' placeholder='Describe function requirements...'></textarea><button onclick='gen()'>Process Request Matrix</button><p id='s' style='color:#fbbf24;display:none;text-align:center;'>Processing custom backprop layers...</p></div><div class='card'><h3>Output:</h3><pre id='o'># Code prints here...</pre></div><div class='card'><h3>Feedback Submission Portal</h3><textarea id='f' placeholder='Report bugs directly to the dashboard...'></textarea><button onclick='fb()'>Submit Feedback</button></div><script>function gen() {{const p=document.getElementById('p').value;if(!p.trim())return;document.getElementById('s').style.display='block';fetch('/generate',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{prompt:p}})}}).then(r=>r.json()).then(d=>{{document.getElementById('s').style.display='none';document.getElementById('o').innerText=d.code||d.message;if(d.code)location.reload();}})}}function fb() {{const f=document.getElementById('f').value;fetch('/feedback',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{message:f}})}}).then(()=>alert('Saved to Database!'))}}</script></body></html>"""

PORTAL_HTML = f"""<!DOCTYPE html><html><head><style>{CSS}</style><title>Access Portal</title></head><body><div class='box card'><h2>{{{{title}}}}</h2>{{% with m=get_flashed_messages() %}}{% if m %}<p style='color:#f87171'>{{{{m}}}}</p>{% endif %}}{{% endwith %}}<form method='POST'><input type='text' name='u' placeholder='Username' required><input type='password' name='p' placeholder='Password' required><button type='submit'>Access Platform</button></form><p style='text-align:center;'>{{% if title=='Login' %}}<a href='/register' style='color:#38bdf8'>Register</a>{{% else %}}<a href='/login' style='color:#38bdf8'>Login</a>{{% endif %}}</p></div></body></html>"""

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    tokens = db.Column(db.Integer, default=15)
    is_premium = db.Column(db.Boolean, default=False)
    last_reset = db.Column(db.DateTime, default=datetime.datetime.utcnow)

class Hist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    prompt = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    message = db.Column(db.Text, nullable=False)

@lm.user_loader
def load_user(uid): 
    return db.session.get(User, int(uid))

def verify_tokens(u):
    if u.is_premium: return
    if (datetime.datetime.utcnow() - u.last_reset).total_seconds() / 3600.0 >= 25.0 and u.tokens < 15:
        u.tokens = 15
        u.last_reset = datetime.datetime.utcnow()
        db.session.commit()

@app.route('/')
@login_required
def dash(): verify_tokens(current_user); return render_template_string(INDEX_HTML)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        u, p = request.form.get('u'), request.form.get('p')
        if User.query.filter_by(username=u).first(): flash('Taken.'); return redirect(url_for('register'))
        db.session.add(User(username=u, password=generate_password_hash(p, method='scrypt')))
        db.session.commit()
        login_user(User.query.filter_by(username=u).first())
        return redirect(url_for('dash'))
    return render_template_string(PORTAL_HTML, title="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(username=request.form.get('u')).first()
        if user and check_password_hash(user.password, request.form.get('p')): login_user(user); return redirect(url_for('dash'))
        flash('Invalid verification credentials.')
    return render_template_string(PORTAL_HTML, title="Login")

@app.route('/logout')
@login_required
def logout(): logout_user(); return redirect(url_for('login'))

@app.route('/generate', methods=['POST'])
@login_required
def gen_code():
    verify_tokens(current_user)
    if current_user.tokens <= 0 and not current_user.is_premium:
        return jsonify({'message': 'Out of tokens. Wait 25 hours or upgrade to Premium.'}), 402
    
    p = request.json.get('prompt', '')
    clean_code = None
    
    # SMART RETRY LOOP: Keeps trying for 45 seconds to let the free AI engine wake up cleanly
    for attempt in range(3):
        try:
            response = requests.post(f"{AI_ENGINE_URL}/compute", json={'prompt': p}, timeout=15)
            clean_code = response.json().get('code')
            if clean_code:
                break
        except Exception:
            time.sleep(15) # Wait 15 seconds for server spinoff initialization before retry

    if not clean_code:
        clean_code = "# The AI Engine is waking up from sleep mode. Please try clicking generate again in 10 seconds."

    if not current_user.is_premium and "waking up" not in clean_code:
        current_user.tokens -= 1
        if current_user.tokens == 0: current_user.last_reset = datetime.datetime.utcnow()
    
    db.session.add(Hist(user_id=current_user.id, prompt=p, response=clean_code))
    db.session.commit()
    return jsonify({'code': clean_code})

@app.route('/feedback', methods=['POST'])
@login_required
def save_feedback():
    m = request.json.get('message', '')
    db.session.add(Feedback(user_id=current_user.id, message=m))
    db.session.commit()
    return jsonify({'status': 'logged'})

@app.route('/stripe-webhook', methods=['POST'])
def webhook():
    payload = request.json
    if payload and payload.get('type') == 'checkout.session.completed':
        email = payload['data']['object'].get('customer_details', {}).get('email')
        try:
            v_session = stripe.checkout.Session.retrieve(payload['data']['object'].get('id'))
            if v_session.payment_status == 'paid':
                u = User.query.filter_by(username=email).first()
                if u: u.is_premium = True; db.session.commit()
        except: pass
    return jsonify({'success': True}), 200

with app.app_context(): 
    db.create_all()

