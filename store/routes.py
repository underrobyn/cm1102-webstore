from flask import render_template, url_for, request, redirect, flash, make_response
from store import app
from store.models import User, Billing, Address, OrderProducts, Orders, Products
from store.forms import CreateForm, LoginForm
from flask_login import login_user, logout_user

# App routes
@app.route("/")
@app.route("/home", methods=['GET'])
def home():
	return render_template('home.html')

@app.route("/account", methods=['GET'])
def account():
	return render_template('account.html')

@app.route("/basket", methods=['GET'])
def basket():
	return render_template('basket.html', title='Basket')

@app.route("/product/<int:product_id>", methods=['GET'])
def product(product_id):
	return render_template('product.html', product_id=product_id)

# Account system routes
@app.route("/create",methods=['GET','POST'])
def create():
	return render_template('create.html', title='Login')

@app.route("/login",methods=['GET','POST'])
def login():
	return render_template('login.html', title='Login')

@app.route("/logout")
def logout():
	logout_user()
	flash('Logout successful!')
	return redirect(url_for('home'))

# Error routes
@app.errorhandler(404)
def not_found(msg):
	return make_response(render_template("error_404.html", msg=msg), 404)