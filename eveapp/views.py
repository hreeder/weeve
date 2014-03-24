from eveapp import app, lm, db, oid
from flask import render_template, flash, redirect, session, url_for, request, g
from flask.ext.login import login_user, logout_user, current_user, login_required
from forms import LoginForm, AddAPIForm, ChangeProfileForm
from models import User, Key, ROLE_USER, ROLE_ADMIN

import evelink
import datetime
from collections import defaultdict
import operator

@lm.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.before_request
def before_request():
    g.user = current_user

@app.route("/")
@app.route("/index")
@app.route("/character/<charid>")
@login_required
def index(charid=0):
    user = g.user
    keys = user.get_keys()
    characters = []
    selected = None
    eve = evelink.eve.EVE()
    tree = eve.skill_tree().result
    sortedtree = ()
    if keys:
        for key in keys:
            api = evelink.api.API(api_key=(key.id, key.vcode))
            acc = evelink.account.Account(api=api)
            chars = acc.characters().result
            training = False
            for char in chars:
                character = evelink.char.Char(api=api, char_id=char)
                csheet = character.character_sheet().result
                ctrain = character.current_training().result
                if ctrain['end_ts'] and int(ctrain['end_ts']) < int(datetime.datetime.utcnow().strftime('%s'))+86400000000:
                    training = True
                characters.append({
                    'id' : char,
                    'keyid' : key,
                    'name' : csheet['name'],
                    'corp' : csheet['corp']['name'],
                    'alliance' : csheet['alliance']['name'],
                    'isk' : csheet['balance'],
                    'sp' : csheet['skillpoints'],
                    'clone' : csheet['clone']['skillpoints'],
                    'current_skill' : ctrain['type_id'],
                    'current_level' : ctrain['level'],
                    'current_finishes' : ctrain['end_ts'],
                    'skills' : csheet['skills']
                })
            for character in characters:
                if training and character['keyid']==key:
                    character['training'] = training
                    
                
        selected = characters[0]
        found = False
        if charid:
            for character in characters:
                if int(character['id']) == int(charid):
                    selected = character
                    found = True
            if not found:
                flash('Unable to select the specified character. If you believe this to be in error, please contact an administrator.')
        stree = defaultdict(dict)
        for group in tree:
            stree[group]['name'] = tree[group]['name']
            stree[group]['id'] = group
            stree[group]['show'] = False
            stree[group]['skills'] = defaultdict(dict)
            stree[group]['count'] = 0
            stree[group]['sp'] = 0
            for skill in tree[group]['skills']:
                selected_skill = next((item for item in selected['skills'] if item['id'] == skill),None)
                if selected_skill:
                    stree[group]['show'] = True
                    stree[group]['skills'][skill] = tree[group]['skills'][skill]
                    stree[group]['skills'][skill]['level'] = selected_skill['level']
                    stree[group]['skills'][skill]['sp'] = selected_skill['skillpoints']
                    stree[group]['sp'] += selected_skill['skillpoints']
                    stree[group]['count'] += 1
                    stree[group]['skills'][skill]['rank'] = tree[group]['skills'][skill]['rank']
            stree[group]['skills'] = sorted(stree[group]['skills'].itervalues(), key=operator.itemgetter('name'))
        sortedtree = sorted(stree.itervalues(), key=operator.itemgetter('name'))
    else:
        flash('You do not currently have any API keys in Weeve. Please add these on your profile.')

    return render_template("index.html", characters=characters, selected=selected, skilltree=sortedtree)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    new_api = AddAPIForm()
    change = ChangeProfileForm()
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
    if change.validate_on_submit():
        current = User.query.filter_by(id=g.user.get_id()).first()
        current.nickname = change.nickname.data
        db.session.add(current)
        db.session.commit()
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
    return render_template("profile.html", new_api=new_api, keys=keys, characters=characters, change_profile=change)

@app.route('/key/delete/<keyid>')
@login_required
def del_key(keyid):
    key = Key.query.filter_by(id=keyid).first()
    if key:
        if key.get_owner().id==g.user.id:
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
        if user == None:
            flash('User %s not found.' % (id))
            return redirect(url_for('index'))
        keys = Key.query.filter_by(user_id=id).all()
        characters = []
        for key in keys:
            try:
                api = evelink.api.API(api_key=(key.id, key.vcode))
                acc = evelink.account.Account(api=api)
                chars = acc.characters().result
                for char in chars:
                    characters.append(chars[char]['name'])
            except evelink.api.APIError, e:
                characters.append(e)
        return render_template('user.html', user=user, characters=characters)
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
