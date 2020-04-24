from store import db
from store.models import *
from random import choice

def rand_digits():
	return ''.join([choice(['1','2','3','4','5','6','7','8','9','0']) for n in range(3)])

def build_sample_db():
	first_names = [
		'Harry', 'Amelia', 'Oliver', 'Jack', 'Isabella', 'Charlie','Sophie', 'Mia',
		'Jacob', 'Thomas', 'Emily', 'Lily', 'Ava', 'Isla', 'Alfie', 'Olivia', 'Jessica',
		'Riley', 'William', 'James', 'Geoffrey', 'Lisa', 'Benjamin', 'Stacey', 'Lucy'
	]
	last_names = [
		'Brown', 'Smith', 'Patel', 'Jones', 'Williams', 'Johnson', 'Taylor', 'Thomas',
		'Roberts', 'Khan', 'Lewis', 'Jackson', 'Clarke', 'James', 'Phillips', 'Wilson',
		'Ali', 'Mason', 'Mitchell', 'Rose', 'Davis', 'Davies', 'Rodriguez', 'Cox', 'Alexander'
	]

	for i in range(len(first_names)):
		fn = choice(first_names)
		ln = choice(last_names)
		
		new_user = User(
			name=fn + " " + ln,
			email=fn.lower() + rand_digits() + "@fake-email.com",
			password="Password123",
			active=1,
			permission_level=1
		)
		db.session.add(new_user)
		print("Added: " + fn + " " + ln)
	
	db.session.commit()
	
build_sample_db()