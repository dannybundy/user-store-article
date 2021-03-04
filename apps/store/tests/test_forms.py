from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
from model_bakery import baker

from store.models import *
from store.forms import *

from .utils.helper_functions import *


class TestQuantityForm(BaseItemTest):
	def test_form_valid(self):
		data = {'quantity': 1}
		form = QuantityForm(data=data)

		self.assertTrue(form.is_valid())

	def test_form_invalid_negative_quantity(self):
		data = {'quantity': -1}
		form = QuantityForm(data=data)

		self.assertFalse(form.is_valid())


class TestStoredAddressForm(BaseAddressTest):
	def test_stored_address(self):
		address = self.address_with_logged_in_customer()

		form = StoredAddressForm(address.customer)
		choices = form.fields['stored_address'].choices	

		value_list = []
		for value, string in choices:
			value_list.append(value)

		self.assertIn(address.pk, value_list)
		self.assertIs(len(value_list), 2)  #includes blank choice



class TestShippingAddressForm(BaseAddressTest):
	def test_save_new_address(self):
		address = baker.make(ShippingAddress, line2="line2")
		customer = baker.make(Customer)
		data = self.address_data(address)

		form = ShippingAddressForm(customer, data)
		form.is_valid()
		address = form.save()

		self.assertEqual(ShippingAddress.objects.all().count(), 2)

	def test_save_with_data_from_already_stored_address_returns_same_address(self):
		address = baker.make(ShippingAddress, line2="line2")
		data = self.address_data(address)

		form = ShippingAddressForm(address.customer, data)
		form.is_valid()
		
		self.assertEqual(form.save().pk, address.pk)
		self.assertEqual(ShippingAddress.objects.all().count(), 1)

	def test_update_successful_returns_address_pk(self):
		address = baker.make(ShippingAddress, line2="line2")
		data = self.address_data(address)		

		form = ShippingAddressForm(address.customer, data)
		form.is_valid()
		
		self.assertEqual(form.update(address), address.pk)


class BillingAddressFormTest(BaseCardTest):
	def test_save_new_card(self):
		card = baker.make(Card, line2="line2")
		customer = baker.make(Customer)
		data = self.card_data(card)

		form = BillingAddressForm(customer, data)
		form.is_valid()
		card = form.save()

		self.assertEqual(Card.objects.all().count(), 2)

	def test_save_with_data_from_already_stored_card_returns_same_card(self):
		card = baker.make(Card, line2="line2")
		data = self.card_data(card)

		form = BillingAddressForm(card.customer, data)
		form.is_valid()
		
		self.assertEqual(form.save().pk, card.pk)
		self.assertEqual(Card.objects.all().count(), 1)

	def test_update_successful_returns_card_pk(self):
		card = baker.make(Card, line2="line2")
		data = self.card_data(card)

		form = BillingAddressForm(card.customer, data)
		form.is_valid()
		
		self.assertEqual(form.update(card), card.pk)