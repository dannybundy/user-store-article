import datetime

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone

from model_bakery import baker

from store.models import *
from store.utils.helper_functions.views import *
from .utils.helper_functions import *


class TestViewsHelperFunctions(BaseItemTest):
	def test_get_chosen_filters(self):
		val = self.items_with_filter_options()
		item_category = val[0]
		filter_option = val[1]

		slug = item_category.slug
		url = reverse('store:item_list', args=(slug,))
		data = {'filter_applied': True, 'filter_option': filter_option.pk}

		response = self.client.get(url, data=data)

		self.assertEqual(get_chosen_filters(response.wsgi_request), [filter_option.pk])

	def test_get_customer_with_guest_num(self):
		item = baker.make(Item)
		url = reverse('store:item_category_list')
		response = self.client.get(url)

		retrieved_customer = get_customer(response.wsgi_request)
		test_customer = Customer.objects.all()[0]

		self.assertEqual(retrieved_customer, test_customer)
		self.assertIsNot(retrieved_customer.guest_num, None)

	def set_item(self):
		self.item = baker.make(Item, quantity=10)
		category_slug = self.item.item_category.slug
		item_slug = self.item.slug

	def test_add(self):
		self.set_item()
		order_item = baker.make(OrderItem, item=self.item)
		user_quantity = order_item.quantity+1

		val = add(order_item, user_quantity)
		msg_success = val[0]
		msg = val[1]

		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertEqual(order_item.quantity, user_quantity)
		self.assertTrue(msg_success)
		self.assertEqual(msg, f"{self.item.name} was added to your cart.")
	
	def test_update(self):
		self.set_item()
		order_item = baker.make(OrderItem, item=self.item, in_cart=True)
		user_quantity = order_item.quantity+1

		val = update(order_item, user_quantity)
		msg_success = val[0]
		msg = val[1]

		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertEqual(order_item.quantity, user_quantity)
		self.assertTrue(msg_success)
		self.assertEqual(msg, "Your cart has been updated.")

	def test_remove(self):
		self.set_item()
		order_item = baker.make(OrderItem, item=self.item, in_cart=True)

		val = remove(order_item)
		msg_success = val[0]
		msg = val[1]

		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertFalse(order_item.in_cart)
		self.assertTrue(msg_success)
		self.assertEqual(msg, f"{self.item.name} has been removed from your cart.")

	def test_card_data(self):
		card = baker.make(Card, line2="line2")
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

		self.assertEqual(card_data(card), data)

	def test_address_data(self):
		address = baker.make(ShippingAddress, line2="line2")
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

		self.assertEqual(address_data(address), data)

	# Not working
	# def test_get_address_forms(self):
	# 	address = baker.make(ShippingAddress, line2="line2")
	# 	customer = address.customer

	# 	test_array = [[
	# 		ShippingAddressForm(
	# 			customer,
	# 			initial=address_data(address)
	# 		),
	# 		address.pk
	# 	]]

	# 	self.assertIn(test_array, get_address_forms(customer))