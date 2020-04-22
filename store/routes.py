from flask import render_template, url_for, request, redirect, flash, make_response
from flask_login import login_user, logout_user, current_user, login_required
from store import app, db, login_manager
from store.models import User
from store.forms import CreateUserForm, LoginUserForm, UpdateEmailForm, UpdatePasswordForm


# App routes
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', title='Product Gallery')


@app.route('/basket', methods=['GET'])
def basket():
    return render_template('basket.html')


@app.route('/checkout', methods=['GET'])
@login_required
def checkout():
    return render_template('checkout.html', title='Checkout')


@app.route('/product/<int:product_id>', methods=['GET'])
def product(product_id):
    return render_template('product.html', product_id=product_id, title='Product Name here')


# Account system routes
@login_manager.unauthorized_handler
def unauthorized():
    flash('You must be logged in to view this page')
    return redirect(url_for('account'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginUserForm()

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


@app.route('/create', methods=['GET', 'POST'])
def create():
    form = CreateUserForm()

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

        flash('Account has been created. You can now login.')

        return redirect(url_for('login'))

    return render_template('create.html', title='Create Account', form=form)


@app.route('/account', methods=['GET'])
@login_required
def account():
    email_form = UpdateEmailForm(prefix="updemail")
    password_form = UpdatePasswordForm(prefix="updpass")

    return render_template('account.html', title='Account', update_email=email_form, update_password=password_form)


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
    return make_response(render_template('error_404.html', msg=msg, title='404 Not Found'), 404)
