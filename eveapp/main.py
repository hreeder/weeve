import json
from flask import Flask, render_template

app = Flask(__name__)

with open("config.json") as fh:
    config=json.loads(fh.read())
assert(config)
app.config.update(config)

@app.template_filter('isk')
def format_currency(value):
    return "{:,.2f}".format(value)

@app.template_filter('sp')
def format_sp(value):
    return "{:,}".format(value)

@app.route("/")
def mainpage():
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
    characters.append(kline)
    
    return render_template("index.html", selected=sklullus, characters=characters)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
