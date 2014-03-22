from eveapp import app, db
import time
import datetime

@app.template_filter('isk')
def format_currency(value):
    return "{:,.2f}".format(value)

@app.template_filter('sp')
def format_sp(value):
    return "{:,}".format(value)

@app.template_filter('skill')
def format_skill(value):
    if value == 1:
        return "I"
    elif value == 2:
        return "II"
    elif value == 3:
        return "III"
    elif value == 4:
        return "IV"
    elif value == 5:
        return "V"

@app.template_filter('itemname')
def format_item(value):
    item = db.engine.execute("SELECT typeName FROM invTypes WHERE typeID = %s" % (value,)).first()
    return item[0]

@app.template_filter('timeuntil')
def format_until(value):
    finish = datetime.datetime.fromtimestamp(value)
    now = datetime.datetime.utcnow()
    diff = finish - now
    return str(diff)#.strftime('%dd %Hh %Mm %Ss')

@app.template_filter('currenttime')
def format_time(value):
    return datetime.datetime.utcnow().strftime("%H:%M")