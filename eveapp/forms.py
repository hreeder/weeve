from flask.ext.wtf import Form
from wtforms import TextField, BooleanField, IntegerField
from wtforms.validators import Required

class LoginForm(Form):
	openid = TextField('openid', validators=[Required()])
	remember_me = BooleanField('remember_me', default = False)

class AddAPIForm(Form):
	userid = IntegerField('userid', validators=[Required()])
	vcode = TextField('vcode', validators=[Required()])