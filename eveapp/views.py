from eveapp import app, lm, db, oid
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import LoginForm, AddAPIForm
from models import User, Key, ROLE_USER, ROLE_ADMIN
import evelink

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
    keys = user.get_keys()
    characters = []
    
    for key in keys:
        api = evelink.api.API(api_key=(key.id, key.vcode))
        acc = evelink.account.Account(api=api)
        chars = acc.characters().result
        for char in chars:
            character = evelink.char.Char(api=api, char_id=char)
            csheet = character.character_sheet().result
            ctrain = character.current_training().result
            characters.append({
                'id' : char,
                'name' : csheet['name'],
                'corp' : csheet['corp']['name'],
                'alliance' : csheet['alliance']['name'],
                'isk' : csheet['balance'],
                'sp' : csheet['skillpoints'],
                'clone' : csheet['clone']['skillpoints'],
                'current_skill' : ctrain['type_id'],
                'current_level' : ctrain['level'],
                'current_remaining' : ctrain['end_ts']
            })

    return render_template("index.html", characters=characters, selected=characters[0])

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    new_api = AddAPIForm()
    if new_api.validate_on_submit():
        try:
            key = Key.query.filter_by(id=new_api.userid.data).first()
            if key is None:
                uid = new_api.userid.data
                vco = new_api.vcode.data
                key = Key(id=uid, vcode=vco, user_id=g.user.get_id())
                db.session.add(key)
                db.session.commit()
                flash('Key %d added' % (uid,), 'success')
            else:
                flash('That key (%d) already exists!' % (new_api.userid.data,))
        except OverflowError, e:
            flash('That caused an error. Please try a valid API again.')
            return redirect(url_for('profile'))
    keys = Key.query.filter_by(user_id=g.user.get_id())
    characters = {}
    for key in keys:
        try:
            api = evelink.api.API(api_key=(key.id, key.vcode))
            acc = evelink.account.Account(api=api)
            chars = acc.characters().result
            characters[key.id] = []
            for char in chars:
                characters[key.id].append(chars[char]['name'])
            characters[key.id] = ', '.join(characters[key.id])
        except evelink.api.APIError, e:
            characters[key.id] = e
    return render_template("profile.html", new_api=new_api, keys=keys, characters=characters)

@app.route('/key/delete/<keyid>')
@login_required
def del_key(keyid):
    key = Key.query.filter_by(id=keyid).first()
    if key:
        if key.get_owner()==g.user.get_id():
            db.session.delete(key)
            db.session.commit()
            return redirect(url_for('profile'))
        else:
            flash("You are unable to remove that key as it does not belong to you. Please contact an Administrator if you believe this is in error.")
            return redirect(url_for('profile'))
    else:
        flash("That key does not exist")
        return redirect(url_for('profile'))

@app.route('/user/<id>')
@login_required
def user(id):
    user = User.query.filter_by(id=id).first()
    if g.user.role == ROLE_ADMIN:
        print user
        if user == None:
            flash('User %s not found.' % (id))
            return redirect(url_for('index'))
        return render_template('user.html', user=user)
    else:
        flash('You are not allowed to access the page of another user')
        return redirect(url_for('index'))

@app.route("/login", methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None and g.user.is_authenticated():
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        return oid.try_login(form.openid.data, ask_for = ['nickname', 'email'])
    return render_template('login.html', form = form, providers = app.config['OPENID_PROVIDERS'])

@app.route("/admin")
@login_required
def show_admin_panel():
    if g.user.role == ROLE_ADMIN:
        return render_template('admin.html')
    else:
        flash('You are not an administrator.')
        return redirect(url_for('index'))

@app.route("/admin/users")
@login_required
def show_admin_users():
    if g.user.role == ROLE_ADMIN:
        users = User.query.all()
        return render_template("users.html", accounts=users)

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