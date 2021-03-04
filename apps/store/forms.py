from crispy_forms.helper import FormHelper

from django import forms
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

from user_profile.models import UserProfile
from user_profile.utils.mixins.forms import CrispyMixin

from .models import *
from .utils.helper_functions.forms import *
from .utils.helper_functions.stripe import *
from .utils.mixins.forms import *


class QuantityForm(CrispyMixin, forms.Form):
	quantity = forms.IntegerField(required=False)

	def clean_quantity(self):
		quantity = self.cleaned_data.get('quantity')
		if quantity < 1:
			raise forms.ValidationError("Enter a valid quantity.")

		return quantity



class StoredAddressForm(CrispyMixin, forms.Form):
	def __init__(self, customer, *args, **kwargs):
		super().__init__(*args, **kwargs)

		self.fields['stored_address'] = forms.ModelChoiceField(
			queryset=ShippingAddress.objects.filter(customer=customer),
			empty_label="",
			widget=forms.Select(attrs={'style': 'width:400px;'})
		)

		if ShippingAddress.objects.filter(customer=customer).count() > 0:
			self.fields['stored_address'].empty_label = "Select Shipping Address"


class StoredCardForm(CrispyMixin, forms.Form):
	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['stored_card'] = forms.ChoiceField(
			choices=stored_card_choices(request),
			widget=forms.Select(
				attrs={'style': 'width:400px;'}
			)
		)


ADDRESS_CHOICES = (
	('Choose Address', 'Choose Address'),
	('Use New Address', 'Use New Address')
)

CARD_CHOICES = (
	('Choose Card', 'Choose Card'),
	('Use New Card', 'Use New Card')
)

class ShippingAddressForm(CrispyCustomerMixin, forms.Form):
	line1 = forms.CharField(
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': '9764 Jeopardy Lane'}
		)
	)
	line2 = forms.CharField(
		required=False,
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': 'Apartment or Suite'}
		)
	)
	city = forms.CharField(
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': 'Chicago'}
		)
	)
	state = forms.CharField(
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': 'IL'}
		)
	)
	zipcode = forms.CharField(
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': '60611'}))

	country = CountryField(
		blank_label='(select country)').formfield(initial='US'
	)

	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	email = forms.EmailField(max_length=30)

	address_option = forms.ChoiceField(
		required=False,
		choices=ADDRESS_CHOICES,
		initial=ADDRESS_CHOICES[0][0],
		widget=forms.RadioSelect()
	)

	def save(self):
		clean = self.cleaned_data
		address = ShippingAddress.objects.get_or_create(
			customer=self.customer,
			line1=clean['line1'],
			line2=clean['line2'],
			city=clean['city'],
			state=clean['state'],
			zipcode=clean['zipcode'],
			country=clean['country'],
			first_name=clean['first_name'],
			last_name=clean['last_name'],
			email=clean['email']
		)[0]
	
		return address

	def update(self, address):
		clean = self.cleaned_data
		address_pk = ShippingAddress.objects.filter(pk=address.pk).update(
			line1=clean['line1'],
			line2=clean['line2'],
			city=clean['city'],
			state=clean['state'],
			zipcode=clean['zipcode'],
			country=clean['country'],
			first_name=clean['first_name'],
			last_name=clean['last_name'],
			email=clean['email']
		)
				
		return address_pk


class BillingAddressForm(CrispyCustomerMixin, forms.Form):
	billing_line1 = forms.CharField(
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder':  '1234 Main St'}
		)
	)
	billing_line2 = forms.CharField(
		required=False,
		max_length=30,
		widget=forms.TextInput(
			attrs={'placeholder': 'Apartment or Suite'}
		)
	)
	billing_city = forms.CharField(max_length=30)
	billing_state = forms.CharField(max_length=30)
	billing_zipcode = forms.CharField(max_length=30)
	billing_country = CountryField(
		blank_label='(select country)'
	).formfield(initial='US')

	billing_first_name = forms.CharField(max_length=30)
	billing_last_name = forms.CharField(max_length=30)
	billing_email = forms.EmailField(max_length=30)

	card_option = forms.ChoiceField(
		required=False,
		choices=CARD_CHOICES,
		initial=CARD_CHOICES[0][0],
		widget=forms.RadioSelect()
	)

	def save(self, stripe_src):
		clean = self.cleaned_data
		val = stripe_add_card(self.customer, stripe_src, clean)

		src_id = val[0]
		new_card = val[1]

		if new_card:
			card = Card.objects.create(
				customer=self.customer,
				src_id=src_id,
				line1=clean['billing_line1'],
				line2=clean['billing_line2'],
				city=clean['billing_city'],
				state=clean['billing_state'],
				zipcode=clean['billing_zipcode'],
				country=clean['billing_country'],
				first_name=clean['billing_first_name'],
				last_name=clean['billing_last_name'],
				email=clean['billing_email']
			)
		else:
			card = Card.objects.get(src_id=src_id)

		return card

	def update(self, card):
		clean = self.cleaned_data
		stripe_update_card(self.customer, card, clean)

		card_pk = Card.objects.filter(pk=card.pk).update(
			line1=clean['billing_line1'],
			line2=clean['billing_line2'],
			city=clean['billing_city'],
			state=clean['billing_state'],
			zipcode=clean['billing_zipcode'],
			country=clean['billing_country'],
			first_name=clean['billing_first_name'],
			last_name=clean['billing_last_name'],
			email=clean['billing_email']
		)

		return card_pk

	def make_payment(self, order, card, address):
		payment_intent_id = make_payment(order, card, address)
		order.record_payment(card, address, payment_intent_id)
		# send_order_email(order)