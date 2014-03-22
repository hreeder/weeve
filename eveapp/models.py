from eveapp import db

ROLE_USER = 0
ROLE_ADMIN = 1


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    role = db.Column(db.SmallInteger, default=ROLE_USER)
    keys = db.relationship('Key', backref='owner', lazy='dynamic')

    def __repr__(self):
        return '<User %r>' % (self.nickname)

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return unicode(self.id)

    def get_keys(self):
        return Key.query.filter_by(user_id=self.id).all()

class Key(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vcode = db.Column(db.String(64))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    characters = db.relationship('Character', backref='key', lazy='dynamic')

    def __repr__(self):
        return '<API Key %r>' % (self.id)

    def get_owner(self):
        return User.query.filter_by(id=self.user_id).first()

    def get_characters(self):
        return Character.query.filter_by(key_id=self.id).all()

class Alliance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    corps = db.relationship('Corp', backref='Alliance', lazy='dynamic')

class Corp(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), index=True)
    allianceid = db.Column(db.Integer, db.ForeignKey('alliance.id'))

class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key_id = db.Column(db.Integer, db.ForeignKey('key.id'))
    name = db.Column(db.String(120), index=True, unique=True)
    corpid = db.Column(db.Integer, db.ForeignKey('corp.id'))
    balance = db.Column(db.Integer)
    sp = db.Column(db.Integer)
    clonesp = db.Column(db.Integer)
