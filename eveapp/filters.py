from eveapp import app

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
