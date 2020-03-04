from datetime import datetime
from store import db

# DB Type information: https://docs.sqlalchemy.org/en/13/core/type_basics.html#generic-types
# Login system information: https://flask-login.readthedocs.io/en/latest/
class User(db.Model):
	# Internal information
	id = db.Column(db.Integer, primary_key=True)
	time_created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

	# Information to be provided by user
	name = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(256), nullable=False)

# TODO: Finish this class
# Each user can have more than one billing card tied to their user
class Billing(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	card_number = db.Column(db.String(16), nullable=False)
	card_name = db.Column(db.String(16), nullable=False)

# TODO: Link to billing and user
class Address(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	postcode = db.Column(db.String(8), nullable=False)
	number = db.Column(db.String(4), nullable=False)
	street = db.Column(db.Text, nullable=False)
	city = db.Column(db.String(25), nullable=False)

class Products(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	time_added = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
	name = db.Column(db.String(100), nullable=False)
	image = db.Column(db.String(30), nullable=False)
	description = db.Column(db.Text, nullable=False)

# Create many-one-many relationship between Products and Orders
class OrderProducts(db.Model):
	order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
	product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
	quantity = db.Column(db.Integer, nullable=False)

# TODO: Add billing and address link
class Orders(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)