import os, secrets, datetime as dt, requests as r, time
from flask import Flask, render_template_string as rt, request as req, redirect as red, url_for as url, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

app = Flask(__name__)
app.config.update(SECRET_KEY=secrets.token_hex(8), SQLALCHEMY_DATABASE_URI='sqlite:///s.db', SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)
lm = LoginManager(app); lm.login_view = 'login'
E_URL = "http://onrender.com" # Change this string to your live app.py URL after deploying to Render

H = """<!DOCTYPE html><html><head><meta charset='UTF-8'><title>AI Pro</title><link href='https://googleapis.com' rel='stylesheet'><style>:root{--bg:#030408;--panel:rgba(13,15,24,0.7);--neon:#00f2fe;--p:#ff007a;--t:#f8fafc;}body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--t);max-width:550px;margin:50px auto;padding:15px;position:relative;overflow-x:hidden;}body::before,body::after{content:'';position:absolute;width:300px;height:300px;border-radius:50%;filter:blur(130px);z-index:-1;opacity:0.25;}body::before{top:-30px;left:-60px;background:var(--neon);}body::after{bottom:-30px;right:-60px;background:#7928ca;}.c{background:var(--panel);backdrop-filter:blur(25px);-webkit-backdrop-filter:blur(25px);padding:25px;border-radius:14px;margin-bottom:20px;border:1px solid rgba(255,255,255,0.05);box-shadow:0 15px 35px rgba(0,0,0,0.5);}h2,h3{font-weight:600;background:linear-gradient(135deg,var(--neon),var(--p));-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:12px;}textarea{width:100%;padding:14px;margin:12px 0;background:#0b0c12;color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-sizing:border-box;font-family:inherit;font-size:0.95rem;height:110px;resize:none;}textarea:focus{outline:none;border-color:var(--neon);box-shadow:0 0 12px rgba(0,242,254,0.25);}button{width:100%;padding:13px;background:linear-gradient(135deg,var(--neon),#7928ca);border:none;color:#000;font-weight:700;border-radius:8px;cursor:pointer;transition:0.2s;font-size:0.95rem;}.bp{background:linear-gradient(135deg,var(--p),#7928ca)!important;color:#fff;}button:hover{transform:translateY(-1px);box-shadow:0 6px 18px rgba(0,242,254,0.35);}.lo{color:#64748b;float:right;text-decoration:none;font-size:0.85rem;padding:5px 10px;border-radius:5px;background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.05);}pre{font-family:'Fira Code',monospace;background:#06070a;padding:16px;color:#34d399;overflow-x:auto;border-radius:8px;white-space:pre-wrap;min-height:120px;font-size:0.9rem;border:1px solid rgba(255,255,255,0.02);line-height:1.5;}.ty::after{content:' █';animation:bk 0.7s infinite;}@keyframes bk{0%,100%{opacity:0}50%{opacity:1}}</style></head><body><div class='c'><a href='/logout' class='lo'>Sign Out</a><h2>AI Terminal Pro 🚀</h2><p style='margin-bottom:15px;'>User Identity: <b>{{current_user.username}}</b> | Tier State: <span style='color:var(--neon);font-weight:bold;'>{%if current_user.is_premium_plus%}👑 Premium Plus{%elif current_user.is_premium%}💎 Premium{%else%}<span id='tc'>{{current_user.tokens}}</span> / 15 Tokens{%endif%}</span></p><div style='display:flex;gap:10px;'><form action='/pay/premium' method='POST' style='flex:1;'><button type='submit'>Premium</button></form><form action='/pay/plus' method='POST' style='flex:1;'><button type='submit' class='bp'>Plus 👑</button></form></div></div><div class='c'><textarea id='p' placeholder='Input computation query rules parameters...'></textarea><button onclick='g()'>Execute Quantum Run ✨</button></div><div class='c'><h3>Output Console Sandbox:</h3><pre id='o'># Matrix Active... Awaiting execution command sequence.</pre></div><script>function g(){const p=document.getElementById('p').value;if(!p.trim())return;const o=document.getElementById('o');o.className="ty";o.innerText="# [0.1s Cache Trigger] Initializing neural logical array blocks...\\n# Mapping sequence similarities inside vector databases...\\n# Syncing memory clusters... Connecting execution pipes...\\n# [System Notice] If backend clusters are resting, total synthesis stream may extend up to 50 seconds to completely awake.";fetch('/gen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({p:p})}).then(r=>r.json()).then(d=>{o.className="";if(d.c){o.innerText=d.c;const s=document.getElementById('tc');if(s&&d.r!==undefined)s.innerText=d.r;}else{o.innerText=d.message;}}).catch(()=>{o.className="";o.innerText='# Core data link timed out. System pipeline lagging. Please re-trigger execute button again.';});}</script></body></html>"""

P = """<!DOCTYPE html><html><head><title>Portal</title><meta charset='UTF-8'><meta name='viewport' content='width=device-width, initial-scale=1.0'><style>body{font-family:sans-serif;background:#030408;color:#fff;max-width:350px;margin:120px auto;padding:15px;}.c{background:rgba(13,15,24,0.85);backdrop-filter:blur(20px);padding:28px;border-radius:14px;border:1px solid rgba(255,255,255,0.05);box-shadow:0 15px 30px rgba(0,0,0,0.5);}h2{text-align:center;background:linear-gradient(135deg,#00f2fe,#ff007a);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:18px;}input{width:100%;padding:12px;margin:8px 0;background:#0b0c12;color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-sizing:border-box;font-size:0.95rem;}button{width:100%;padding:13px;background:linear-gradient(135deg,#00f2fe,#7928ca);border:none;color:#000;font-weight:bold;border-radius:8px;cursor:pointer;margin-top:8px;font-size:1rem;}a{color:#00f2fe;text-decoration:none;display:block;text-align:center;margin-top:14px;font-size:0.9rem;}</style></head><body><div class='c'><h2>Portal {{t}}</h2>{%with m=get_flashed_messages()%}{%if m%}{%for msg in m%}<p style='color:#ff007a;text-align:center;font-size:0.85rem;margin-bottom:10px;'>{{msg}}</p>{%endfor%}{%endif%}{%endwith%}<form method='POST'><input type='text' name='u' placeholder='Username' required><input type='password' name='p' placeholder='Password' required><button type='submit'>Verify Access Key</button></form>{%if t=='Login'%}<a href='/register'>Create New Account</a>{%else%}<a href='/login'>Return to Portal Login</a>{%endif%}</div></body></html>"""

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True); username = db.Column(db.String(150), unique=True, nullable=False); password = db.Column(db.String(256), nullable=False)
    tokens = db.Column(db.Integer, default=15); is_premium = db.Column(db.Boolean, default=False); is_premium_plus = db.Column(db.Boolean, default=False); last_reset = db.Column(db.DateTime, default=dt.datetime.utcnow)

@lm.user_loader
def load_user(uid): return db.session.get(User, int(uid))
def v_tok(u):
    if u.is_premium or u.is_premium_plus: return
    if (dt.datetime.utcnow() - u.last_reset).total_seconds() / 3600.0 >= 25.0 and u.tokens < 15: u.tokens = 15; u.last_reset = dt.datetime.utcnow(); db.session.commit()

@app.route('/')
@login_required
def dash(): v_tok(current_user); return rt(H)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if req.method == 'POST':
        u, p = req.form.get('u'), req.form.get('p')
        if User.query.filter_by(username=u).first(): flash('Occupied.'); return red(url('register'))
        db.session.add(User(username=u, password=gh(p, method='scrypt'))); db.session.commit()
        login_user(User.query.filter_by(username=u).first()); return red(url('dash'))
    return rt(P, t="Register")

@app.route('/login', methods=['GET', 'POST'])
def login():
    if req.method == 'POST':
        user = User.query.filter_by(username=req.form.get('u')).first()
        if user and ch(user.password, req.form.get('p')): login_user(user); return red(url('dash'))
        flash('Invalid credentials.')
    return rt(P, t="Login")

@app.route('/logout')
@login_required
def logout(): logout_user(); return red(url('login'))

@app.route('/gen', methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens <= 0 and not current_user.is_premium and not current_user.is_premium_plus: return jsonify({'message': 'Expired tokens.'}), 402
    p = req.json.get('p', ''); cc = None
    for _ in range(2):
        try:
            res = r.post(E_URL + "/compute", json={'prompt': p}, timeout=15); cc = res.json().get('code')
            if cc: break
        except: time.sleep(5)
    if not cc: cc = "# AI Engine waking up from deep sleep mode.\\n# Please try clicking run button again in 10 seconds."
    if not current_user.is_premium and not current_user.is_premium_plus and "waking up" not in cc:
        current_user.tokens -= 1
        db.session.commit()
    return jsonify({'c': cc, 'r': current_user.tokens})

@app.route('/pay/premium', methods=['POST'])
@login_required
def pay_premium(): return red("https://stripe.com", code=33)

@app.route('/pay/plus', methods=['POST'])
@login_required
def pay_plus(): return red("https://stripe.com", code=33)

if __name__ == '__main__':
    with app.app_context(): db.create_all()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
