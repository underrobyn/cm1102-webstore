from flask import render_template, url_for, request, redirect, flash, make_response, session
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import create_engine

from store import app, db, login_manager
import flask_sqlalchemy
from store.models import User, Products, Address, Basket, BasketItems
from store.forms import CreateUserForm, LoginUserForm, UpdateEmailForm, UpdatePasswordForm, AddToCart, AddAddressForm


# App routes
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
    return render_template('home.html', title='Product Gallery')


@app.route('/addcart', methods=["POST"])
def AddCart():
    form = AddToCart()

    try:
        product_id = request.form.get("product_id")
        amount = request.form.get('amount')
        quantity = amount
        product = Products.query.filter_by(id=product_id).first()
        print(amount)
        if product_id and amount and request.method== "POST":
            DictCart = {product_id: {'name':product.name, 'price':product.price, 'quantity':amount}}

            if 'ShopBasket' in session:
                session['ShopBasket'] = DictCart
                print(session['ShopBasket'])

                basket = BasketItems(product_id=product_id,quantity=amount,basket_id=current_user.id)
                db.session.add(basket)
                db.session.commit()


            else:
                session['ShopBasket'] = DictCart
                return redirect(request.referrer)
    except Exception as e:
        print(e)
    finally:
        return redirect(request.referrer)


@app.route('/basket', methods=['GET'])
def basket():
    addCart = AddToCart()
    currentBasket = BasketItems.query.all()
    print(currentBasket)
    products = Products.query.all()
    return render_template('basket.html', cart=currentBasket, products=products, form=addCart)


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
            password=form.password.data,
            active=1,
            permission_level=1
        )

        db.session.add(new_user)
        db.session.flush()

        new_basket = Basket(
            user_id=new_user.id
        )

        db.session.add(new_basket)
        db.session.commit()

        flash('Account has been created. You can now login.')

        return redirect(url_for('login'))

    return render_template('create.html', title='Create Account', form=form)


@app.route('/account', methods=['GET'])
@login_required
def account():
    email_form = UpdateEmailForm(prefix="updemail")
    password_form = UpdatePasswordForm(prefix="updpass")

    if email_form.validate_on_submit():
        print(email_form)

    if password_form.validate_on_submit():
        print(password_form)

    return render_template('account.html', title='Account', update_email=email_form, update_password=password_form)


@app.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
    if request.args.get('remove'):
        remove_id = request.args.get('remove')
        address_data = Address.query.filter_by(id=remove_id).first()
        if not address_data:
            return forbidden("You attempted to remove an address that does not exist")

    addresses = Address.query.filter_by(user_id=current_user.id).all()
    address_form = AddAddressForm(prefix="addaddr")

    if address_form.validate_on_submit():
        new_address = Address(
            user_id=current_user.id,
            postcode=address_form.postcode.data,
            houseid=address_form.houseid.data,
            street=address_form.street.data,
            city=address_form.city.data
        )

        db.session.add(new_address)
        db.session.commit()

        flash('Address has been added to your account.')

    return render_template('billing.html', title='Billing Information', add_address=address_form, address_list=addresses)


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        flash('You must be logged in to log out!')
    else:
        logout_user()
        flash('You have been logged out!')

    return redirect(url_for('login'))


# Error routes
@app.errorhandler(403)
def forbidden(msg):
    return make_response(render_template('error_403.html', msg=msg, title='403 Forbidden'), 403)


@app.errorhandler(404)
def not_found(msg):
    return make_response(render_template('error_404.html', msg=msg, title='404 Not Found'), 404)
