from flask import render_template, url_for, request, redirect, flash
from store import app
from store.models import User

@app.route("/")
@app.route("/home")
def home():
  return render_template('home.html')

