import datetime
import os
import sys
from flask import (Flask, redirect, render_template, request,
                   session, url_for, jsonify)
import requests
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_jsglue import JSGlue
import json
import traceback
from tempfile import mkdtemp

# helpers dependencies
import string
import random

# scraper dependencies
from bs4 import BeautifulSoup
import re

# Own directory
from helpers import Helpers
from config import get_keys
from scraper import ScheduleScraper

settings = get_keys(os)


helpers_dependencies = dict(random=random, string=string)
helpers = Helpers(settings, **helpers_dependencies)

scraper_dependencies = dict(get=requests.get, BeautifulSoup=BeautifulSoup, re=re)
scraper = ScheduleScraper(**scraper_dependencies)

settings['SECRET_KEY'] = os.environ.get('SECRET_KEY', helpers.get_salt(25))

app = Flask(__name__)

# required for datad url_for
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')
app.static_path = STATIC_ROOT

jsglue = JSGlue(app)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['TEMPLATES_AUTO_RELOAD'] = True

app.config.update({
    'SECRET_KEY': os.environ.get('SECRET_KEY', settings.get('SECRET_KEY'))
})


if app.config["DEBUG"]:
    @app.after_request
    def after_request(response):
        response.headers["Cache-Control"] = (
            "no-cache, no-store," +
            " must-revalidate")
        response.headers["Expires"] = 0

        response.headers["Pragma"] = "no-cache"
        return response

sess = Session()
sess.init_app(app)

"""
    app.context_processor modifies the *url_for* flask static file server
    to append ?q= + dateTime hash.
    This allows for cache busting of static files
"""


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):

    if endpoint == 'static':
        filename = values.get('filename', None)
        if filename:
            file_path = os.path.join(app.root_path, app.static_path, filename)
            values['q'] = int(os.stat(file_path).st_mtime)

    # endpoint = endpoint + root if root not in endpoint else endpoint
    return url_for(endpoint, **values)


""""""
@app.route('/', methods=["POST", "GET"])
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    username = session.get("username")
    return render_template("index.html", username = username)

@app.route("/get_data")
def get_data():
    data = "hello world"
    return jsonify({"status": "success", "data" : data})

@app.route('/login')
def login():

    if request.method == "POST":
        session["username"] = request.form.get("username")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect( url_for("login"))

@app.route("/add_numbers/<int:num1>/<int:num2>", methods=["Get"])
def add_numbers(num1, num2):

    return jsonify({"answer" : int(num1) + int(num2)})


if __name__ == '__main__':
    app.debug = True
    port = int(os.environ.get("PORT", 5000))
    app.run(host='127.0.0.1', port=port)
