from eveapp import app, db
import time
import datetime

@app.template_filter('isk')
def format_currency(value):
    return "{:,.2f}".format(value)

@app.template_filter('sp')
def format_sp(value):
    return "{:,}".format(value)

@app.template_filter('totalsp')
def format_totalsp(value):
    totalsp = 256000 * value
    return "{:,}".format(totalsp)

@app.template_filter('skill')
def format_skill(value):
    if value == "0" or value == None or value == 0:
        return "0"
    elif value == 1:
        return "I"
    elif value == 2:
        return "II"
    elif value == 3:
        return "III"
    elif value == 4:
        return "IV"
    elif value == 5:
        return "V"
    else:
        return value

@app.template_filter('itemname')
def format_item(value):
    if value == None:
        return "None"
    item = db.engine.execute("SELECT typeName FROM invTypes WHERE typeID = %s" % (value,)).first()
    return item[0]

@app.template_filter('time')
def format_time(value):
    time = datetime.datetime.utcfromtimestamp(value)
    return time.strftime("%a %d %b - %H:%M EvE")

@app.template_filter('timeuntil')
def format_until(value):
    finish = datetime.datetime.utcfromtimestamp(value)
    now = datetime.datetime.utcnow()
    diff = finish - now
    out = []

    if diff.days:
        out.append("%sd" % (diff.days))

    # Calc number of hours
    h = diff.seconds // 3600
    if h:
        out.append("%dh" % (int(h)))
    # Take that number of hours away from our seconds
    s = diff.seconds - (h*3600)
    # calc number of minutes
    m = s // 60
    if m:
        out.append("%dm" % (int(m)))
    # Take that number of minutes away from our seconds
    s = s - (m*60)
    # Append the remainder
    if s:
        out.append("%ds" % (int(s)))
    # Join the list together for nice formatting
    return " ".join(out)

@app.template_filter('currenttime')
def format_time(value):
    return datetime.datetime.utcnow().strftime("%H:%M")
