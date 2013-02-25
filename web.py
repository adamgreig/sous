# -*- coding: utf-8 -*-

import json
import sqlite3
from flask import Flask, request, g

app = Flask(__name__, static_folder="./html", static_url_path="")

@app.route("/config", methods=["GET", "POST"])
def get_config():
    cur = g.db.cursor()
    if request.method == "POST":
        config = request.json
        if not config:
            return "ERR no valid config received"
        cur.execute("INSERT INTO config VALUES (null, ?, ?, ?)",
                    (config["food"], config["temp"], config["time"]))
        g.db.commit()
        return "OK"
    else:
        cur.execute("SELECT * FROM config ORDER BY id DESC LIMIT 1")
        cfg = cur.fetchone()
        return json.dumps({"food": cfg[1], "temp": cfg[2], "time": cfg[3]})

@app.route("/data", methods=["GET", "POST"])
def get_data():
    cur = g.db.cursor()
    if request.method == "POST":
        data = request.json
        if not data:
            return "ERR no valid data received"
        print "data:",data
        cur.execute("INSERT INTO data VALUES (?, ?, ?)", data)
        g.db.commit()
        return "OK"
    else:
        n = int(request.args.get('since', 0))
        cur.execute("SELECT * FROM data ORDER BY time LIMIT -1 OFFSET ?", (n,))
        data = cur.fetchall()
        if not data:
            return json.dumps([[], []])
        times, temps, powers = zip(*data)
        temps = zip(times, temps)
        powers = zip(times, powers)
        return json.dumps([temps, powers])

@app.route("/")
def index():
    with open("html/index.html") as f:
        page = f.read()
    return page

@app.before_request
def before_req():
    g.db = sqlite3.connect("data.sqlite")

@app.teardown_request
def teardown_req(exception):
    if hasattr(g, 'db'):
        g.db.close()

if __name__ == "__main__":
    db = sqlite3.connect("data.sqlite")
    cur = db.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS data "
                "(time REAL, temp REAL, power INTEGER)")
    cur.execute("CREATE TABLE IF NOT EXISTS config "
                "(id INTEGER PRIMARY KEY, food TEXT(64), temp REAL,"
                " time INTEGER)")
    app.run(host='0.0.0.0', debug=True)
