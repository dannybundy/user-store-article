import random, string

from django.shortcuts import redirect

from store.forms import ShippingAddressForm, BillingAddressForm
from store.models import *
from .stripe import stripe_retrieve_card


def get_chosen_filters(request):
	"""returns a list of PKs"""

	filter_applied = request.GET.get('filter_applied')
	if filter_applied is not None:

		pk_list = request.GET.getlist('filter_option', [])
		for i in range(0, len(pk_list)):
			pk_list[i] = int(pk_list[i])

		request.session['pk_list'] = pk_list
	else:
		# Clicked on pagination
		pk_list = request.session.get('pk_list', [])

	return pk_list


def get_customer(request):
	guest_num = request.session.get('guest_num')

	if request.user.is_authenticated:
		customer = Customer.objects.get_or_create(user=request.user)[0]
	
	elif guest_num is not None:
		customer = Customer.objects.get_or_create(guest_num=guest_num)[0]
	
	else:
		guest_num = 0
		guest_qs = Customer.objects.filter(guest_num__isnull=False)
		
		if guest_qs.exists():
			recent_guest_num = guest_qs.order_by('-guest_num')[0].guest_num
			guest_num = recent_guest_num+1
		
		request.session['guest_num'] = guest_num
		customer = Customer.objects.create(guest_num=guest_num)

	return customer


def add(order_item, user_quantity):
	item_name = order_item.item.name

	if order_item.in_cart:
		msg = f"{item_name} is already in your cart."
		return [False, msg]

	valid_quantity = order_item.handle_quantity(user_quantity)

	if valid_quantity is None:
		msg = f"No {item_name} in stock."
		return [False, msg]

	elif not valid_quantity:
		msg = f"""Not enough {item_name} in stock. However we added the amount
		we have to your cart.
		"""
		return [False, msg]

	else:
		msg = f"{item_name} was added to your cart."

	return [True, msg]


def update(order_item, user_quantity):
	item_name = order_item.item.name

	if not order_item.in_cart:
		msg = f"{item_name} is not in your cart."
		return [False, msg]

	valid_quantity = order_item.handle_quantity(user_quantity)

	if valid_quantity is None:
		msg = f"No {item_name} in stock."
		return [False, msg]
	
	elif not valid_quantity:
		msg = f"""Not enough {item_name} in stock. However we updated your cart with
		the amount we have.
		"""
		return [False, msg]
	else:
		msg = "Your cart has been updated."
		return [True, msg]


def remove(order_item):
	item_name = order_item.item.name

	if not order_item.in_cart:
		msg = f"{item_name} is not in your cart."
		return [False, msg]

	order_item.remove_from_cart()
	msg = f"{item_name} has been removed from your cart."

	return [True, msg]


def card_data(card):
	data = {
		'billing_line1': card.line1,
		'billing_line2': card.line2,
		'billing_city': card.city,
		'billing_state': card.state,
		'billing_zipcode': card.zipcode,
		'billing_country': card.country,
		'billing_first_name': card.first_name,
		'billing_last_name': card.last_name,
		'billing_email': card.email
	}
	return data


def card_info(stripe_card):
	data = {
		'brand': stripe_card.card.brand,
		'last4': stripe_card.card.last4,
		'exp_month': stripe_card.card.exp_month,
		'exp_year': stripe_card.card.exp_year
	}
	return data


def address_data(address):
	data = {
		'line1': address.line1,
		'line2': address.line2,
		'city': address.city,
		'state': address.state,
		'zipcode': address.zipcode,
		'country': address.country,
		'first_name': address.first_name,
		'last_name': address.last_name,
		'email': address.email
	}
	return data



def get_address_forms(customer):
	form_list = []
	for address in ShippingAddress.objects.filter(customer=customer):
		form_list.append([
			ShippingAddressForm(
				customer,
				initial=address_data(address)
			),
			address.pk
		])
	return form_list


def get_billing_forms(customer):
	form_list = []
	for card in Card.objects.filter(customer=customer):
		stripe_card = stripe_retrieve_card(card)

		form_list.append([BillingAddressForm(
			customer,
			initial=card_data(card)),
			card.pk,
			card_info(stripe_card)
		])

	return form_list