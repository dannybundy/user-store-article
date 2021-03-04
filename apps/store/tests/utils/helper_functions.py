from django.test import TestCase

from model_bakery import baker
from store.models import *



class BaseItemTest(TestCase):
	def default_order_item(self):
		order = baker.make(Order)
		item = baker.make(Item, price=10, quantity=20)
		order_item = baker.make(
			OrderItem,
			customer=order.customer,
			order=order,
			item=item,
		)
		return order_item

	def order_item_in_cart(self):
		order_item = self.default_order_item()
		order_item.in_cart = True
		order_item.quantity = 2
		order_item.save()

		return order_item

	def order_item_ordered(self):
		order_item = self.order_item_in_cart()
		order_item.ordered = True
		order_item.save()

		return order_item


	def order_with_order_items_in_cart(self):
		order_item = self.order_item_in_cart()
		order = order_item.order
		customer = order_item.customer

		for i in range(0, 5):
			order_item = baker.make(
				OrderItem,
				customer=customer,
				order=order,
				quantity=2,
				in_cart=True,
			)

		return order


	def order_with_order_items_ordered(self):
		order = self.order_with_order_items_in_cart()

		for order_item in order.orderitem_set.all():
			order_item.ordered = True
			order_item.save()

		return order


	def default_item_category(self):
		date_2_days_ago = timezone.now() - relativedelta(days=2)
		item_category = baker.make(ItemCategory,
			date_started=date_2_days_ago,
		)
		return item_category



	def items_with_filter_options(self):
		item_category = baker.make(ItemCategory)

		for i in range(0, 5):
			filter_category = baker.make(FilterCategory, item_category=item_category)
			filter_option = baker.make(FilterOption, filter_category=filter_category)

			item = baker.make(Item, item_category=item_category)
			item.filter_option.add(filter_option)
			item.save()

		return [item_category, filter_option]




class BaseAddressTest(TestCase):
	def address_with_logged_in_customer(self):
		user = baker.make(User)
		customer = Customer.objects.get(user=user)
		address = baker.make(
			ShippingAddress,
			customer=customer,
			line2='line2'
		)

		self.client.force_login(user)

		return address

	def address_data(self, address):
		data = {
			'line1': address.line1,
			'line2': address.line2,
			'city': address.city,
			'state': address.state,
			'zipcode': address.zipcode,
			'country': address.country,
			'first_name': address.first_name,
			'last_name': address.last_name,
			'email': address.email,
		}
		return data


class BaseCardTest(TestCase):
	def card_with_logged_in_customer(self):
		user = baker.make(User)
		customer = Customer.objects.get(user=user)
		card = baker.make(
			Card,
			customer=customer,
			line2="line2"
		)

		self.client.force_login(user)

		return card

	def card_data(self, card):
		data = {
			'src_id': card.src_id,
			'billing_line1': card.line1,
			'billing_line2': card.line2,
			'billing_city': card.city,
			'billing_state': card.state,
			'billing_zipcode': card.zipcode,
			'billing_country': card.country,
			'billing_first_name': card.first_name,
			'billing_last_name': card.last_name,
			'billing_email': card.email,
		}
		return data