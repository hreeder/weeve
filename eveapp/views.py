from eveapp import app, lm, db, oid
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import LoginForm, AddAPIForm
from models import User, ROLE_USER, ROLE_ADMIN

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route("/")
@app.route("/index")
@login_required
def index():
    user = g.user
    characters = []

    sklullus = {}
    sklullus['id'] = 445518960
    sklullus['name'] = "Sklullus Dromulus"
    sklullus['corp'] = "Sniggerdly"
    sklullus['alliance'] = "Pandemic Legion"
    sklullus['isk'] = 2607720370.31
    sklullus['sp'] = 39607624
    sklullus['clone'] = 42200000
    sklullus['current_skill'] = "Logistics"
    sklullus['current_level'] = 5
    sklullus['current_remaining'] = "23d 8h"

    characters.append(sklullus)

    kline = {}
    kline['id'] = 92029019
    kline['name'] = "Kline Eto"
    kline['corp'] = "B0rthole"
    kline['alliance'] = None
    kline['isk'] = 1000000000.00
    kline['sp'] = 40000000
    kline['clone'] = 64000000
    kline['current_skill'] = "Jump Drive Calibration"
    kline['current_level'] = 3
    kline['current_remaining'] = 8

    characters.append(kline)
    
    return render_template("index.html", selected=sklullus, characters=characters)

@app.route('/profile')
@login_required
def profile():
    new_api = AddAPIForm()
    return render_template("profile.html", new_api=new_api)

@app.route('/user/<email>')
@login_required
def user(email):
    user = User.query.filter_by(email=email).first()
    if g.user is not None and g.user.is_authenticated() and g.user.role == ROLE_ADMIN:
        if user == None:
            flash('User %s not found.' % (email))
            return redirect(url_for('index'))
        return render_template('user.html', user=user)
    else:
        flash('You are not allowed to access the page of another user')
        return redirect(url_for('index'))

@app.route("/login", methods = ['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', form = form, providers = app.config['OPENID_PROVIDERS'])

@oid.after_login
def after_login(resp):
    if resp.email is None or resp.email == "":
        flash('Invalid login. Please try again.')
        return redirect(url_for('login'))
    user = User.query.filter_by(email = resp.email).first()
    if user is None:
        nickname = resp.nickname
        if nickname is None or nickname == "":
            nickname = resp.email.split('@')[0]
        user = User(nickname=nickname, email=resp.email, role=ROLE_USER)
        db.session.add(user)
        db.session.commit()
    remember_me = False
    if 'remember_me' in session:
        remember_me = session['remember_me']
        session.pop('remember_me', None)
    login_user(user, remember=remember_me)
    return redirect(request.args.get('next') or url_for('index'))

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))