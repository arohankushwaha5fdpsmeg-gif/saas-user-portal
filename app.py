import os,secrets,datetime as dt,requests as r,time;from flask import Flask,render_template_string as rt,request as req,redirect as red,url_for as url,flash,jsonify;from flask_sqlalchemy import SQLAlchemy;from flask_login import LoginManager,UserMixin,login_user,logout_user,login_required,current_user;from werkzeug.security import generate_password_hash as gh,check_password_hash as ch;import stripe
app=Flask(__name__);app.config.update(SECRET_KEY=secrets.token_hex(8),SQLALCHEMY_DATABASE_URI=os.environ.get('postgresql://aisaasdb_user:z5GyV7u7ppPCZqqa0DoSH3TjjhWDgTnz@dpg-d94kar67r5hc73f89ks0-a/aisaasdb','sqlite:///s.db'),SQLALCHEMY_TRACK_MODIFICATIONS=False);db=SQLAlchemy(app);lm=LoginManager(app);lm.login_view='login'
stripe.api_key="sk_test_51Tke3WRsVgVw9kTXB7nWOrvb1jGUnCuTAqwgcX5OA7r7hxVh534pcyg5Y0D989GwT4CQmwsfN9SezJyb8gEdjXDF00OEi2JoDS"
E_URL="https://onrender.com"

# REMOVED PYTHON F-STRING TO PREVENT ALL BRACKET PARSING SYNTAX ERRORS PERMANENTLY
H="""<!DOCTYPE html><html><head><style>body{font-family:sans-serif;background:#0f172a;color:#fff;max-width:500px;margin:20px auto;padding:10px}.c{background:#1e293b;padding:15px;border-radius:6px;margin-bottom:10px}input,textarea{width:100%;padding:8px;margin:5px 0;background:#0f172a;color:#fff;border:1px solid #475569;border-radius:6px;box-sizing:border-box}button{width:100%;padding:10px;background:#38bdf8;border:none;color:#0f172a;font-weight:bold;border-radius:6px;cursor:pointer}.bp{background:#ec4899;color:#fff}</style><title>AI</title></head><body><div class='c'><a href='/logout' style='color:#94a3b8;float:right;text-decoration:none;'>Logout</a><h2>AI Dashboard Pro 🚀</h2>
<p>User: <b>{{current_user.username}}</b> | Tier: <span style='color:#38bdf8;font-weight:bold;'>{%if current_user.is_premium_plus%}👑 Premium Plus{%elif current_user.is_premium%}💎 Premium{%else%}<span id='tc'>{{current_user.tokens}}</span> / 15{%endif%}</span></p>
<div style='display:flex;gap:10px;'>
<form action='/pay/premium' method='POST' style='flex:1;'><button type='submit' style='background:#7c3aed;color:#fff;'>Premium</button></form>
<form action='/pay/plus' method='POST' style='flex:1;'><button type='submit' class='bp'>Premium Plus 👑</button></form>
</div>
{%if not current_user.is_premium and not current_user.is_premium_plus and current_user.tokens <= 0%}
<div style='background:#ef4444;padding:10px;border-radius:6px;text-align:center;margin-top:10px;'>⚠️ Tokens exhausted. Resets in 25h.</div>
{%endif%}</div><div class='c'><textarea id='p' placeholder='Prompt...'></textarea><button onclick='g()'>Run ✨</button><p id='s' style='color:#fbbf24;display:none;text-align:center;'>🤖 Processing matrix arrays...</p></div>
<div class='c'><h3>Output:</h3><pre id='o' style='background:#020617;padding:10px;color:#34d399;overflow-x:auto;border-radius:6px;white-space:pre-wrap;'># Code will stay visible here safely...</pre><button style='background:#10b981;color:#fff;width:auto;' onclick='cp()'>Copy 📋</button></div>
<div class='c'><h3>Feedback</h3><textarea id='f'></textarea><button onclick='fb()'>Submit</button></div><script>
function g(){
    const p=document.getElementById('p').value;
    if(!p.trim())return;
    document.getElementById('s').style.display='block';
    fetch('/gen',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({p:p})
    }).then(r=>r.json()).then(d=>{
        document.getElementById('s').style.display='none';
        if(d.c){
            document.getElementById('o').innerText=d.c;
            const s=document.getElementById('tc');
            if(s&&d.r!==undefined)s.innerText=d.r;
        }else{
            document.getElementById('o').innerText=d.message;
        }
    }).catch(e=>{
        document.getElementById('s').style.display='none';
        document.getElementById('o').innerText='# Server connection lagging. Try again.';
    });
}
function cp(){navigator.clipboard.writeText(document.getElementById('o').innerText);alert('Copied!');}
function fb(){const f=document.getElementById('f').value;if(!f.trim())return;fetch('/fb',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({m:f})}).then(()=>{alert('Saved!');document.getElementById('f').value='';});}
</script></body></html>"""

P="""<!DOCTYPE html><html><head><style>body{font-family:sans-serif;background:#0f172a;color:#fff;max-width:500px;margin:20px auto;padding:10px}.c{background:#1e293b;padding:15px;border-radius:6px;margin-bottom:10px}input,textarea{width:100%;padding:8px;margin:5px 0;background:#0f172a;color:#fff;border:1px solid #475569;border-radius:6px;box-sizing:border-box}button{width:100%;padding:10px;background:#38bdf8;border:none;color:#0f172a;font-weight:bold;border-radius:6px;cursor:pointer}</style><title>Portal</title></head><body><div class='c'><h2>{{t}}</h2>{%with m=get_flashed_messages()%}{%if m%}<p style='color:#f87171'>{{ m }}</p>{%endif%}{%endwith%}<form method='POST'><input type='text' name='u' placeholder='Username' required><input type='password' name='p' placeholder='Password' required><button type='submit'>Submit</button></form><p style='text-align:center;'>{%if t=='Login'%}<a href='/register' style='color:#38bdf8;text-decoration:none;'>Create Account</a>{%else%}<a href='/login' style='color:#38bdf8;text-decoration:none;'>Login Here</a>{%endif%}</p></div></body></html>"""

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True);username=db.Column(db.String(150),unique=True,nullable=False);password=db.Column(db.String(256),nullable=False);tokens=db.Column(db.Integer,default=15);is_premium=db.Column(db.Boolean,default=False);is_premium_plus=db.Column(db.Boolean,default=False);last_reset=db.Column(db.DateTime,default=dt.datetime.utcnow)
class Hist(db.Model):id=db.Column(db.Integer,primary_key=True);user_id=db.Column(db.Integer,nullable=False);prompt=db.Column(db.Text,nullable=False);response=db.Column(db.Text,nullable=False)
class Feedback(db.Model):id=db.Column(db.Integer,primary_key=True);user_id=db.Column(db.Integer,nullable=False);message=db.Column(db.Text,nullable=False)
@lm.user_loader
def load_user(uid):return db.session.get(User,int(uid))
def v_tok(u):
    if u.is_premium or u.is_premium_plus:return
    if (dt.datetime.utcnow()-u.last_reset).total_seconds()/3600.0>=25.0 and u.tokens<15:u.tokens=15;u.last_reset=dt.datetime.utcnow();db.session.commit()
@app.route('/')
@login_required
def dash():v_tok(current_user);return rt(H)
@app.route('/register',methods=['GET','POST'])
def register():
    if req.method=='POST':
        u,p=req.form.get('u'),req.form.get('p')
        if User.query.filter_by(username=u).first():flash('Taken.');return red(url('register'))
        db.session.add(User(username=u,password=gh(p,method='scrypt')));db.session.commit();login_user(User.query.filter_by(username=u).first());return red(url('dash'))
    return rt(P,t="Register")
@app.route('/login',methods=['GET','POST'])
def login():
    if req.method=='POST':
        user=User.query.filter_by(username=req.form.get('u')).first()
        if user and ch(user.password,req.form.get('p')):login_user(user);return red(url('dash'))
        flash('Invalid credentials.')
    return rt(P,t="Login")
@app.route('/logout')
@login_required
def logout():logout_user();return red(url('login'))
@app.route('/gen',methods=['POST'])
@login_required
def gen_code():
    v_tok(current_user)
    if current_user.tokens <= 0 and not current_user.is_premium and not current_user.is_premium_plus:return jsonify({'message': 'Expired tokens.'}),402
    p=req.json.get('p','');cc=None
    for _ in range(2):
        try:
            res=r.post(E_URL+"/compute",json={'prompt':p},timeout=15);cc=res.json().get('code')
            if cc:break
        except:time.sleep(5)
    if not cc:cc="# AI Engine waking up from deep sleep mode. Please try clicking run button again in 10 seconds."
    if not current_user.is_premium and not current_user.is_premium_plus and "waking up" not in cc:
        current_user.tokens-=1
        if current_user.tokens==0:current_user.last_reset=dt.datetime.utcnow()
        db.session.commit()
    db.session.add(Hist(user_id=current_user.id,prompt=p,response=cc));db.session.commit()
    return jsonify({'c':cc,'r':current_user.tokens})
@app.route('/fb',methods=['POST'])
@login_required
def save_fb():db.session.add(Feedback(user_id=current_user.id,message=req.json.get('m','')));db.session.commit();return jsonify({'status':'ok'})
@app.route('/pay/premium',methods=['POST'])
@login_required
def pay_premium():
    s=stripe.checkout.Session.create(line_items=[{'price_data':{'currency':'usd','product_data':{'name':'Premium Tier'},'unit_amount':2500},'quantity':1}],mode='payment',success_url=req.host_url,cancel_url=req.host_url,customer_email=current_user.username)
    return red(s.url,code=33)
@app.route('/pay/plus',methods=['POST'])
@login_required
def pay_plus():
    s=stripe.checkout.Session.create(line_items=[{'price_data':{'currency':'usd','product_data':{'name':'Premium Plus Tier'},'unit_amount':4900},'quantity':1}],mode='payment',success_url=req.host_url,cancel_url=req.host_url,customer_email=current_user.username)
    return red(s.url,code=33)
@app.route('/stripe-webhook',methods=['POST'])
def webhook():
    payload=req.json
    if payload and payload.get('type')=='checkout.session.completed':
        session_obj=payload['data']['object'];email=session_obj.get('customer_details',{}).get('email');item_name=session_obj.get('line_items',[{}]).get('description','')
        u=User.query.filter_by(username=email).first()
        if u:
            if "Plus" in item_name or session_obj.get('amount_total')==4900:u.is_premium_plus=True
            else:u.is_premium=True
            db.session.commit()
    return jsonify({'success':True}),200
with app.app_context():db.create_all()
