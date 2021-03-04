import stripe

from django.conf import settings
from django.contrib import messages
from store.models import Card


PUB_KEY = settings.STRIPE_PUBLISHABLE_KEY
stripe.api_key = settings.STRIPE_SECRET_KEY


def stripe_error(request):
	try:
		go_to_exceptions
	# Since it's a decline, stripe.error.warning will be caught
	except stripe.error.CardError as e:
		body = e.json_body
		err = body.get('warning',{})
		messages.warning(request, f"{err.get('message')}")

	# Too many requests made to the API too quickly
	except stripe.error.RateLimitError as e:
		messages.warning(request, "Rate limite error")

	# Invalid parameters were supplied to Stripe's API
	except stripe.error.InvalidRequestError as e:
		messages.warning(request, "Invalid Parameters")

	# Authentication with Stripe's API failed
	# (maybe you changed API keys recently)
	except stripe.error.AuthenticationError as e:
		messages.warning(request, "Not authenticated")

	# Network communication with Stripe failed
	except stripe.error.APIConnectionError as e:
		messages.warning(request, "Network warning")

	# Display a very generic warning to the user, and maybe send
	# yourself an email
	except stripe.error.StripeError as e:
		messages.warning(request, "Something went wrong. You were not charged. Please try again.")

	# Other warning
	except Exception as e:
		messages.warning(request, "An unknown error occurred. We have been notified.")


# Used in "StoredCardForm"
def stored_card_choices(customer):
	card_list = Card.objects.filter(customer=customer)
	
	CARD_CHOICES = []
	initial_choice = ('', '')
	if card_list.exists():
		for i in range(0, len(card_list)):
			try:
				retrieved_card = stripe.Source.retrieve(card_list[i].src_id)['card']
			except:
				return (('', "Error: Refresh Page"),)

			card_info = f"""{retrieved_card['brand']}: **** **** **** {retrieved_card['last4']} 
			| exp-date: {retrieved_card['exp_month']}/{retrieved_card['exp_year']}"""
			
			CARD_CHOICES.append([card_list[i].pk, card_info])
			
			if i == 0:
				CARD_CHOICES[i][1] += ' (Default)'

		initial_choice = ('', 'Select Card')


	CARD_CHOICES.insert(0, initial_choice)

	return CARD_CHOICES


# Used in "BillingForm"
def stripe_add_card(customer, stripe_src, clean):
	if customer.stripe_customer_id is not None:
		customer_id = customer.stripe_customer_id
	else:
		customer_id = stripe.Customer.create(
			name=customer.full_name,
			email=customer.email,
		)['id']
		customer.stripe_customer_id = customer_id
		customer.save()

	card = stripe.Source.retrieve(stripe_src)
	fingerprint = card.card.fingerprint
	exp_month = card.card.exp_month
	exp_year = card.card.exp_year

	# Get all Stripe cards
	card_list = stripe.Customer.list_sources(customer_id,)['data']

	# If card exists
	for card in card_list:
		if (
			card['card']['fingerprint'] == fingerprint and
			card['card']['exp_month'] == exp_month and
			card['card']['exp_year'] == exp_year
		):
			src_id = card['id']
			return [src_id, False]

	# If not, create new source
	src_id = stripe.Customer.create_source(customer_id, source=stripe_src,).id
	stripe.Customer.modify_source(
		customer_id,
		src_id,
		owner={
			'name': f"{clean['billing_first_name']}, {clean['billing_last_name']}",
			'email': clean['billing_email'],
			'address': {
				'line1': clean['billing_line1'],
				'line2': clean['billing_line2'],
				'city': clean['billing_city'],
				'state': clean['billing_state'],
				'postal_code': clean['billing_zipcode'],	
				'country': clean['billing_country'],
			}			
		}
	)
	return [src_id, True]


def stripe_update_card(customer, card, clean):
	stripe.Customer.modify_source(
		customer.stripe_customer_id,
		card.src_id,
		owner={
			'name': f"{clean['billing_first_name']}, {clean['billing_last_name']}",
			'email': clean['billing_email'],
			'address': {
				'line1': clean['billing_line1'],
				'line2': clean['billing_line2'],
				'city': clean['billing_city'],
				'state': clean['billing_state'],
				'postal_code': clean['billing_zipcode'],	
				'country': clean['billing_country'],
			}			
		}
	)


def make_payment(order, card, address):
	description_str = order.get_order_description()[1]

	# Initiate payment
	payment_intent_id = stripe.PaymentIntent.create(
		description=description_str,
		amount=int(order.get_price_total()*100),
		currency='usd',
		customer=order.customer.stripe_customer_id,
	)['id']


	# Confirm payment
	stripe.PaymentIntent.confirm(
		payment_intent_id,
		payment_method=card.src_id,
		shipping={
			'name': f"{address.first_name}, {address.last_name}",
			'address': {
				'line1': address.line1,
				'line2': address.line2,
				'city': address.city,
				'state': address.state,
				'postal_code': address.zipcode,
				'country': address.country,
			}
		}
	)
	

	return payment_intent_id

# Used in "ItemDetailView" and "OrderSummaryView"
def stripe_delete_card(customer, card):
	stripe.Customer.delete_source(
		customer.stripe_customer_id,
		card.src_id
	)


# Used in "get_billing_forms" in "help_functions.views"
def stripe_retrieve_card(card):
	return stripe.Source.retrieve(card.src_id)
