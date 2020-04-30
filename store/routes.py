from flask import render_template, url_for, request, redirect, flash, make_response, session, send_from_directory
from flask_login import login_user, logout_user, current_user, login_required
from sqlalchemy import create_engine

from store import app, db, login_manager
import flask_sqlalchemy, os, time, json
from store.models import User, Products, Address, Basket, BasketItems, Billing, BillingAddress, Orders, OrderProducts, \
	ProductReviews
from store.forms import CreateUserForm, LoginUserForm, UpdateEmailForm, UpdatePasswordForm, AddToCart, AddAddressForm, \
	DeleteAccountForm, DownloadDataForm, InputBillingForm, ProductReviewForm, DeleteFromCart


# App routes
@app.route('/')
@app.route('/home', methods=['GET'])
def home():
	products = Products.query.all()

	if len(request.args) != 0:
		if request.args.get('search_products'):
			search_query = '%' + request.args.get('search_products') + '%'
			products = Products.query.filter(Products.name.like(search_query)).all()

	return render_template('home.html', title='Product Gallery', products=products)


@app.route('/addcart', methods=["POST"])
@login_required
def AddCart():
	form = AddToCart()

	if form.validate_on_submit():
		product_id = request.form.get("product_id")
		quantity = int(form.quantity.data)

		# Check product exists
		try:
			product = Products.query.filter_by(id=product_id).first()
			if not product or not product_id:
				flash("Item does not exist")
				return redirect(request.referrer)

			basket = Basket.query.filter_by(user_id=current_user.id).first()

			# Adding product to cart if quantity <250
			if quantity and 0 < quantity <= 250:
				basket_item = BasketItems(basket_id=basket.id, product_id=product_id, quantity=quantity)
				db.session.add(basket_item)
				db.session.commit()

				flash("Item added to basket")
				return redirect(url_for("basket"))
			else:
				flash("The quantity you entered was too large")
				return redirect("basket")

		except Exception as e:
			print(e)
			flash("Item not added to basket")
			return redirect(url_for("basket"))
	else:
		flash("Item not added to basket")
		return redirect(url_for("basket"))


@app.route('/basket', methods=['GET', 'POST'])
@login_required
def basket():
	delete_form = DeleteFromCart()
	basket_data = Basket.query.filter_by(user_id=current_user.id).first()

	# Clear all Cart
	if request.method == 'POST':
		if delete_form.validate_on_submit():
			basket_items = BasketItems.query.filter_by(basket_id=basket_data.id).all()
			for item in basket_items:
				db.session.delete(item)
			db.session.commit()

			flash("Shopping Basket Cleared!")

	# Delete individual item
	if request.args.get('delete_item'):
		basket_item_id = request.args.get('delete_item')
		basket_product = BasketItems.query.filter_by(id=basket_item_id, basket_id=basket_data.id).first()
		db.session.delete(basket_product)
		db.session.commit()
		flash("Item removed from Basket!")

	products = Products.query.all()
	shoppingDict = {}
	items = BasketItems.query.filter_by(basket_id=basket_data.id).all()

	# Create dict for jinja
	for item in items:
		product = Products.query.filter_by(id=item.product_id).first()
		if product.id in shoppingDict.keys():
			list = shoppingDict[product.id]
			quant = int(list[1]) + item.quantity
			subtotal = int(quant * product.price)
			shoppingDict[product.id] = [product.name, quant, product.price, subtotal, product.image, item.id]
		else:
			subtotal = int(item.quantity * product.price)
			shoppingDict[product.id] = [product.name, item.quantity, product.price, subtotal, product.image, item.id]

	# Calculate total
	total = 0
	item_count = 0
	for item in shoppingDict.values():
		total = total + item[3]
		item_count = item_count + item[1]

	page_title = '[%s] Basket' % item_count

	return render_template('basket.html', title=page_title, cart=shoppingDict, products=products, form=delete_form, totalprice=total, totalitems=item_count)


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
	form = InputBillingForm()

	# Get addresses
	addresses = Address.query.filter_by(user_id=current_user.id).all()
	if len(addresses) == 0:
		# redirect to billing#
		flash('You must have a saved address to access checkout.')
		return redirect(url_for('billing'))

	# Get basket
	total = 0
	basket = Basket.query.filter_by(user_id=current_user.id).first()
	item_list = BasketItems.query.filter_by(basket_id=basket.id).all()

	if len(item_list) == 0:
		flash('You must have items in your basket to checkout.')
		return redirect(url_for('home'))

	for item in item_list:
		itemData = Products.query.filter_by(id=item.product_id).first()
		total = total + (itemData.price * item.quantity)

	if request.method == "POST":
		if form.validate_on_submit():
			if len(form.card_number.data) != 16 or len(form.card_cvc.data) != 3 or len(form.card_end.data) != 5:
				flash('Invalid card information entered. Please enter card information in the format shown')
			else:
				# Add card to billing card table
				new_billing = Billing(
					card_number=form.card_number.data,
					card_cvc=form.card_cvc.data,
					card_end=form.card_end.data
				)
				db.session.add(new_billing)
				db.session.flush()

				# Add billing address
				new_billingaddr = BillingAddress(
					billing_id=new_billing.id,
					address_id=request.form.get('billing_addr')
				)
				db.session.add(new_billingaddr)
				db.session.flush()

				new_order = Orders(
					delivery_address_id=request.form.get('delivery_addr'),
					billing_id=new_billingaddr.id
				)
				db.session.add(new_order)
				db.session.flush()

				for basket_item in item_list:
					add_product_order = OrderProducts(
						order_id=new_order.id,
						product_id=basket_item.product_id,
						quantity=basket_item.quantity
					)
					db.session.add(add_product_order)
					db.session.delete(basket_item)
					db.session.flush()

				db.session.commit()

				flash('Order has been placed. Thank you for shopping!')
				return redirect(url_for('home'))

	return render_template('checkout.html', addresses=addresses, billing=form, total=total, title='Checkout')


@app.route('/product/<int:product_id>', methods=['GET'])
def product(product_id):
	cart_form = AddToCart()
	product_reviews = ProductReviews.query.filter_by(product_id=product_id).all()
	product_info = Products.query.filter_by(id=product_id).first()

	return render_template('product.html', product=product_info, reviews=product_reviews, add_cart=cart_form, title='Product Name here')


@app.route('/reviews/<int:product_id>', methods=['GET', 'POST'])
def reviews(product_id):
	product_info = Products.query.filter_by(id=product_id).first()
	add_review_form = ProductReviewForm()

	if add_review_form.validate_on_submit():
		new_review = ProductReviews(
			rating=add_review_form.rating.data,
			review=add_review_form.review.data,
			product_id=product_id,
			user_id=current_user.id
		)
		db.session.add(new_review)
		db.session.commit()

		flash("Your review of " + product_info.name + " has been added!")

	# Check if the user wishes to remove one of their reviews
	if request.args.get('remove'):
		remove_id = request.args.get('remove')
		review_data = ProductReviews.query.filter_by(id=remove_id).first()

		# Check the address exists
		if not review_data:
			flash("You cannot delete that review")

		# Check that this address belongs to the logged in user
		elif review_data.user_id != current_user.id:
			flash("You cannot delete that review.")

		else:
			db.session.delete(review_data)
			db.session.commit()
			flash("Removed your review of " + product_info.name)

	review_data = []
	product_reviews = ProductReviews.query.filter_by(product_id=product_id).all()
	for review in product_reviews:
		user_info = User.query.filter_by(id=review.user_id).first()

		# Check if the user has purchased this product in the past
		user_purchased_product = False
		user_orders = db.session.query(Orders).join(Address).filter(Address.user_id == review.user_id)
		for order in user_orders:
			curr_order = OrderProducts.query.filter_by(product_id=review.product_id, order_id=order.id).all()
			if curr_order:
				user_purchased_product = True
				break

		review_data.append({
			"id": review.id,
			"reviewer": user_info.name,
			"curr_user": user_info.id == current_user.id,
			"time": review.time_added.strftime("%Y/%m/%d, %H:%M"),
			"rating": review.rating,
			"review": review.review,
			"purchased": user_purchased_product
		})

	return render_template('reviews.html', product=product_info, reviews=review_data, add_review=add_review_form,
	                       title='Reviews for ' + product_info.name)


# Account system routes
@login_manager.unauthorized_handler
def unauthorized():
	flash('You must be logged in to view this page')
	return redirect(url_for('login'))


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


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
	email_form = UpdateEmailForm(prefix="updemail")
	password_form = UpdatePasswordForm(prefix="updpass")
	account_delete_form = DeleteAccountForm(prefix="delacc")
	account_data_form = DownloadDataForm(prefix="dlacc")

	# If this is a post request then we have a lot of work to do...
	if request.method == "POST":
		update_user = User.query.filter_by(id=current_user.id).first()

		if email_form.validate_on_submit():
			entered_email = email_form.email.data
			entered_pass = email_form.password.data

			# Check if email already in use
			results = User.query.filter_by(email=entered_email).all()
			if len(results) > 0:
				flash("This email is already in use by somebody else")
				return redirect(url_for('account'))

			# Check password is correct
			if not current_user.verify_password(entered_pass):
				flash("Account password was incorrect.")
				return redirect(url_for('account'))

			update_user.email = entered_email
			db.session.commit()

			flash("Email was updated!")

		if password_form.validate_on_submit():
			entered_pass = password_form.password.data
			entered_newpass = password_form.new_password.data

			# Check password is correct
			if not current_user.verify_password(entered_pass):
				flash("Current password was incorrect.")
				return redirect(url_for('account'))

			update_user.password = entered_newpass
			db.session.commit()

			flash("Password was updated!")

		if account_delete_form.validate_on_submit():
			entered_pass = account_delete_form.password.data
			entered_consent = account_delete_form.confirm_delete.data

			# Check password is correct
			if not current_user.verify_password(entered_pass):
				flash("Account password was incorrect.")
				return redirect(url_for('account'))

			if not entered_consent:
				flash("Please give consent for the account to be deleted")
				return redirect(url_for('account'))

			# Delete user basket
			user_basket = Basket.query.filter_by(user_id=current_user.id).first()
			basket_items = BasketItems.query.filter_by(basket_id=user_basket.id).all()
			for item in basket_items:
				db.session.delete(item)
			db.session.delete(user_basket)
			db.session.flush()

			# Delete user addresses
			user_addresses = Address.query.filter_by(user_id=current_user.id).all()
			for address in user_addresses:
				db.session.delete(address)
			db.session.flush()

			# Delete user account
			db.session.delete(update_user)

			# Save changes to db
			db.session.commit()

			# Logout user
			flash("Your account has been deleted.")
			logout_user()
			return redirect(url_for('login'))

	return render_template('account.html', title='Account', update_email=email_form, update_password=password_form,
	                       delete_account=account_delete_form, download_data=account_data_form)


@app.route('/billing', methods=['GET', 'POST'])
@login_required
def billing():
	# Check if the user wishes to remove an address
	if request.args.get('remove'):
		remove_id = request.args.get('remove')
		address_data = Address.query.filter_by(id=remove_id).first()

		# Check the address exists
		if not address_data:
			flash("You cannot delete that address.")
			return redirect(url_for("billing"))

		# Check that this address belongs to the logged in user
		if address_data.user_id != current_user.id:
			flash("You cannot delete that address.")
			return redirect(url_for("billing"))

		db.session.delete(address_data)
		db.session.commit()

		flash("Removed address")
		return redirect(url_for("billing"))

	# Check if we need to add an address
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
		redirect(url_for("billing"))

	# Get a list of this users addresses
	addresses = Address.query.filter_by(user_id=current_user.id).all()

	return render_template('billing.html', title='Billing Information', add_address=address_form,
	                       address_list=addresses)


@app.route('/orders', methods=['GET'])
def orders():
	order_dict = {}

	user_orders = db.session.query(Orders).join(Address).filter(Address.user_id == current_user.id)
	for order in user_orders:
		products = []
		total = 0

		curr_order = OrderProducts.query.filter_by(order_id=order.id).all()
		for order_product in curr_order:
			curr_product = Products.query.filter_by(id=order_product.product_id).first()
			products.append({
				"id": order_product.product_id,
				"name": curr_product.name,
				"price": curr_product.price,
				"quantity": order_product.quantity,
				"total": order_product.quantity * curr_product.price,
				"image": curr_product.image
			})
			total = total + curr_product.price * order_product.quantity

		order_dict[order.id] = {
			"id": order.id,
			"products": products,
			"total": total,
			"time": order.time.strftime("%Y/%m/%d, %H:%M"),
		}

	return render_template('orders.html', title='Order History', orders=order_dict)


@app.route('/gdpr_download', methods=['POST'])
def gdpr_download():
	account_data_form = DownloadDataForm(prefix="dlacc")

	# Check user password
	if account_data_form.validate_on_submit():
		entered_pass = account_data_form.password.data

		# Check password is correct
		if not current_user.verify_password(entered_pass):
			flash("Current password was incorrect.")
			return redirect(url_for('account'))

	# Get user information from database
	addresses = Address.query.filter_by(user_id=current_user.id).all()
	basket = Address.query.filter_by(user_id=current_user.id).first()
	basket_items = BasketItems.query.filter_by(basket_id=basket.id).all()

	def get_product_info(product_id):
		inf = Products.query.filter_by(id=product_id).first()
		return {
			"name": inf.name,
			"description": inf.description,
			"style": inf.style,
			"price": inf.price
		}

	order_info = {}
	address_info = []
	for addr in addresses:
		address_info.append({
			"postcode": addr.postcode,
			"house": addr.houseid,
			"street": addr.street,
			"city": addr.city
		})

		# Get order details
		get_order = Orders.query.filter_by(delivery_address_id=addr.id).all()
		for order in get_order:
			products_in_order = OrderProducts.query.filter_by(order_id=order.id).all()
			for order_info in products_in_order:
				product_inf = get_product_info(order_info.product_id)
				order_info[order.id] = product_inf
				order_info[order.id]["total"] = product_inf["price"] * order_info.quantity

	output_data = {
		"UserAccountInformation": [{
			"time_registered": current_user.time_created.isoformat(),
			"name": current_user.name,
			"email": current_user.email
		}],
		"UserAddressInformation": address_info,
		"UserOrderInformation": order_info
	}

	html_data = json.dumps(output_data)

	# Create download
	path = os.path.join(app.root_path, app.config['DL_FOLDER'])
	filename = "user_" + str(current_user.id) + "_" + str(time.time()) + ".html"
	f = open(path + "/" + filename, "w+")
	f.write(html_data)
	f.close()

	return send_from_directory(directory=path, filename=filename)


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
