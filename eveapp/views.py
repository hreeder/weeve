from eveapp import app
from flask import Flask, render_template

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