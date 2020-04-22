from flask import url_for, request, redirect, flash
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from store.models import User, Billing, Address, OrderProducts, Orders, Products
from store import admin, db


class AdminView(ModelView):
	list_template = 'admin_templates/list.html'
	edit_template = 'admin_templates/edit.html'
	create_template = 'admin_templates/create.html'

	def is_accessible(self):
		if current_user.is_authenticated:
			if current_user.get_id():
				user = User.query.get(current_user.get_id())
				return True

		return False

	def inaccessible_callback(self, name, **kwargs):
		flash("You are not logged in as an administrator")
		return redirect(url_for('login', next=request.url))


class UsersView(AdminView):
	column_exclude_list = ['password_hash', ]
	column_searchable_list = ['name', 'email']


# Admin views
admin.add_view(UsersView(User, db.session))  # , category="User Data"
admin.add_view(AdminView(Billing, db.session))
admin.add_view(AdminView(Address, db.session))
admin.add_view(AdminView(OrderProducts, db.session))
admin.add_view(AdminView(Orders, db.session))
admin.add_view(AdminView(Products, db.session))
