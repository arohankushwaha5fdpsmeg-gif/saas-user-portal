import os, secrets, datetime as dt, requests as r, time
from flask import Flask, render_template_string as rt, request as req, redirect as red, url_for as url, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash as gh, check_password_hash as ch

app = Flask(__name__)
app.config.update(SECRET_KEY=secrets.token_hex(8), SQLALCHEMY_DATABASE_URI='sqlite:///s.db', SQLALCHEMY_TRACK_MODIFICATIONS=False)
db = SQLAlchemy(app)
lm = LoginManager(app); lm.login_view = 'login'
E_URL = "http://localhost:5001" # Switch to your App 1 Render URL when deploying both

# --- HIGH-PREMIUM MINI GLASS DASHBOARD INTERFACE ---
H = """<!DOCTYPE html><html><head><meta charset="UTF-8"><title>AI Pro</title>
<link href="https://googleapis.com" rel="stylesheet">
<style>
:root{--bg:#06070d;--neon:#00f2fe;--pink:#ec4899;--txt:#f1f5f9;}
body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--txt);max-width:520px;margin:40px auto;padding:15px;position:relative;}
body::before{content:'';position:absolute;width:250px;height:250px;background:var(--neon);filter:blur(130px);z-index:-1;opacity:0.2;top:10%;left:15%;}
.c{background:rgba(16,18,27,0.8);backdrop-filter:blur(10px);padding:20px;border-radius:12px;margin-bottom:15px;border:1px solid rgba(255,255,255,0.04);box-shadow:0 10px 30px rgba(0,0,0,0.5);}
h2,h3{background:linear-gradient(135deg,var(--neon),#9d4edd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;margin-bottom:10px;}
textarea{width:100%;padding:12px;margin:8px 0;background:#141622;color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-sizing:border-box;}
textarea:focus{outline:none;border-color:var(--neon);box-shadow:0 0 10px rgba(0,242,254,0.2);}
button{width:100%;padding:12px;background:linear-gradient(135deg,var(--neon),#9d4edd);border:none;color:#000;font-weight:bold;border-radius:8px;cursor:pointer;transition:0.2s;}
button:hover{transform:translateY(-1px);box-shadow:0 5px 12px rgba(0,242,254,0.3);}
.bp{background:var(--pink)!important;color:#fff;}
pre{font-family:'Fira Code',monospace;background:#08090f;padding:14px;color:#34d399;overflow-x:auto;border-radius:8px;white-space:pre-wrap;min-height:100px;font-size:0.9rem;}
.typing::after{content:' █';animation:b 0.8s infinite;}@keyframes b{0%,100%{opacity:0}50%{opacity:1}}
</style></head><body>
<div class='c'><a href='/logout' style='color:#64748b;float:right;text-decoration:none;font-size:0.85rem;'>Logout</a>
<h2>AI Dashboard Pro 🚀</h2><p>User: <b>{{current_user.username}}</b> | Tier: <span style='color:var(--neon);font-weight:bold;'>
{%if current_user.is_premium_plus%}👑 Premium Plus{%elif current_user.is_premium%}💎 Premium{%else%}<span id='tc'>{{current_user.tokens}}</span> / 15 Tokens{%endif%}</span></p>
<div style='display:flex;gap:10px;margin-top:10px;'>
<form action='/pay/premium' method='POST' style='flex:1;'><button type='submit'>Premium</button></form>
<form action='/pay/plus' method='POST' style='flex:1;'><button type='submit' class='bp'>Plus 👑</button></form>
</div></div>
<div class='c'><textarea id='p' placeholder='Input query code requirements logic...'></textarea><button onclick='g()'>Run Compute Engine ✨</button></div>
<div class='c'><h3>Output Terminal:</h3><pre id='o'># System Core Matrix Terminal Online Ready...</pre></div>
<script>
function g(){
    const p=document.getElementById('p').value;if(!p.trim())return;
    const o=document.getElementById('o');o.className="typing";
    o.innerText="# Instantly generating powerful dynamic synthesis parameters...\\n# Syncing mathematical logic structures...\\n# [Note] If backend server is waking up, response loop may take 50 seconds.";
    fetch('/gen',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({p:p})})
    .then(r=>r.json()).then(d=>{o.className="";if(d.c){o.innerText=d.c;const s=document.getElementById('tc');if(s&&d.r!==undefined)s.innerText=d.r;}else{o.innerText=d.message;}})
    .catch(()=>{o.className="";o.innerText='# Target pipeline lag. Try again in a brief moment.';});
}
</script></body></html>"""

P = """<!DOCTYPE html><html><head><title>Portal</title><style>body{font-family:sans-serif;background:#06070d;color:#fff;max-width:350px;margin:100px auto;padding:15px;}.c{background:#10121b;padding:25px;border-radius:12px;border:1px solid rgba(255,255,255,0.04);box-shadow:0 10px 30px rgba(0,0,0,0.5);}h2{text-align:center;background:linear-gradient(135deg,#00f2fe,#9d4edd);-webkit-background-clip:text;-webkit-text-fill-color:transparent;}input{width:100%;padding:12px;margin:8px 0;background:#141622;color:#fff;border:1px solid rgba(255,255,255,0.08);border-radius:8px;box-sizing:border-box;}button{width:100%;padding:12px;background:linear-gradient(135deg,#00f2fe,#9d4edd);border:none;color:#000;font-weight:bold;border-radius:8px;cursor:pointer;margin-top:8px;}a{color:#00f2fe;text-decoration:none;display:block;text-align:center;margin-top:12px;font-size:0.9rem;}</style></head><body><div class='c'><h2>Portal {{t}}</h2>{%with m=get_flashed_messages()%}{%if m%}{%for msg in m%}<p style='color:#f87171;text-align:center;font-size:0.85rem;'>{{msg}}</p>{%endfor%}{%endif%}{%endwith%}<form method='POST'><input type='text' name='u' placeholder='Username' required><input type='password' name='p' placeholder='Password' required><button type='submit'>Authenticate</button></form>{%if t=='Login'%}<a href='/register'>Create Account</a>{%else%}<a href='/login'>Login</a>{%endif%}</div></body></html>"""

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

