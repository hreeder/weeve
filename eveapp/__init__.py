from flask import Flask

app = Flask(__name__)
from eveapp import views, filters

app.config.from_object('config')