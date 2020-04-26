from datetime import datetime
from store import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# DB Type information: https://docs.sqlalchemy.org/en/13/core/type_basics.html#generic-types
# Login system information: https://flask-login.readthedocs.io/en/latest/
class User(UserMixin, db.Model):
	# Internal information
	id = db.Column(db.Integer, primary_key=True)
	time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	# Information to be provided by user
	name = db.Column(db.String(50), nullable=False)
	password_hash = db.Column(db.String(128))
	password = db.Column(db.String(60), nullable=False)
	email = db.Column(db.String(256), unique=True, nullable=False)
	active = db.Column(db.Integer, nullable=False)
	permission_level = db.Column(db.Integer, nullable=False)

	@property
	def password(self):
		raise AttributeError("You cannot read the password attribute")

	@password.setter
	def password(self, password):
		self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)

	def verify_password(self, password):
		return check_password_hash(self.password_hash, password)

	def __unicode__(self):
		return self.name


@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))


# Each user can have more than one billing card tied to their user
class Billing(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	card_number = db.Column(db.String(16), nullable=False)
	card_cvc = db.Column(db.String(8), nullable=False)
	card_end = db.Column(db.String(16), nullable=False)


class BillingAddress(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	billing_id = db.Column(db.Integer, db.ForeignKey('billing.id'), nullable=False)
	address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)


class Address(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	postcode = db.Column(db.String(8), nullable=False)
	houseid = db.Column(db.Text, nullable=False)
	street = db.Column(db.Text, nullable=False)
	city = db.Column(db.String(25), nullable=False)


class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	time_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(100), nullable=False)
	image = db.Column(db.String(30), nullable=False)
	description = db.Column(db.Text, nullable=False)
	size = db.Column(db.String(20), nullable=False, default="Medium")
	weight = db.Column(db.Float, nullable=False)
	style = db.Column(db.String(30), nullable=False)
	price = db.Column(db.Integer, nullable=False)


# Create many-one-many relationship between Products and Orders
class OrderProducts(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	quantity = db.Column(db.Integer, nullable=False)


class Orders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	delivery_address_id = db.Column(db.Integer, db.ForeignKey('address.id'), nullable=False)
	billing_id = db.Column(db.Integer, db.ForeignKey('billing_address.id'), nullable=False)


class Basket(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	items = db.relationship('BasketItems', backref='basket', lazy=True)


class BasketItems(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	basket_id = db.Column(db.Integer, db.ForeignKey('basket.id'))
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	quantity = db.Column(db.Integer, nullable=False)
