from flask import render_template, url_for, request, redirect, flash, make_response
from store import app, admin, db, login_manager
from store.models import User, Billing, Address, OrderProducts, Orders, Products
from store.forms import CreateForm, LoginForm
from flask_login import login_user, logout_user, current_user, login_required
from flask_admin.contrib.sqla import ModelView


# App routes
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html')


@app.route('/account', methods=['GET'])
@login_required
def account():
    return render_template('account.html')


@app.route('/basket', methods=['GET'])
def basket():
    return render_template('basket.html')


@app.route('/checkout', methods=['GET'])
@login_required
def checkout():
    return render_template('checkout.html')


@app.route('/product/<int:product_id>', methods=['GET'])
def product(product_id):
    return render_template('product.html', product_id=product_id)


# Admin views
admin.add_view(ModelView(User, db.session))
admin.add_view(ModelView(Billing, db.session))
admin.add_view(ModelView(Address, db.session))
admin.add_view(ModelView(OrderProducts, db.session))
admin.add_view(ModelView(Orders, db.session))
admin.add_view(ModelView(Products, db.session))


# Account system routes
@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view this page')
    return redirect(url_for('account'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if current_user.is_authenticated:
        flash('You are already logged in!')
        return redirect(url_for('account'))

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is None:
            flash('Invalid email address')
        elif not user.verify_password(form.password.data):
            flash('Invalid password')
        else:
            login_user(user)
            flash('You have been logged in')
            return redirect(url_for('home'))

        return render_template('login.html', title='Login', form=form)

    return render_template('login.html', title='Login', form=form)


@app.route('/create',methods=['GET','POST'])
def create():
    form = CreateForm()

    if current_user.is_authenticated:
        flash('You cannot complete this action whilst logged in!')
        return redirect(url_for('account'))

    if form.validate_on_submit():
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data
        )

        db.session.add(new_user)
        db.session.commit()

        flash('Account created')

        return redirect(url_for('home'))

    return render_template('create.html', title='Create Account', form=form)


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        flash('You must be logged in to log out!')
    else:
        logout_user()
        flash('You have been logged out!')

    return redirect(url_for('login'))


# Error routes
@app.errorhandler(404)
def not_found(msg):
    return make_response(render_template('error_404.html', msg=msg), 404)