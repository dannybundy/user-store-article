from django.contrib.auth.models import User
from django.core import mail
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.utils import timezone

from dateutil.relativedelta import *
from model_bakery import baker
from unittest import mock

from store.models import *
from user_profile.models import UserProfile
from .utils.helper_functions import *


class TestCustomerModel(TestCase):
	def test_create_customer_when_user_is_created(self):
		user = baker.make(User)
		customer_qs = Customer.objects.filter(user=user)
		customer = customer_qs[0]

		self.assertEqual(customer_qs.exists(), True)
		self.assertEqual(customer.full_name, f"{user.first_name} {user.last_name}")
		self.assertEqual(customer.email, user.email)
		self.assertEqual(customer.guest_num, None)

	def test_create_guest_customer_when_no_user_attached_to_customer(self):
		customer = baker.make(Customer)
		self.assertEqual(customer.guest_num, 0)

	def test_str(self):
		customer = baker.make(Customer)
		self.assertEqual(str(customer), customer.full_name)

	# def test_stripe_time_dif(self):
	# 	customer = baker.make(Customer)
		
	# 	self.assertEqual(
	# 		customer.stripe_time_dif(),
	# 		(timezone.now()-customer.purchase_attempt_time).total_seconds()
	# 	)

	def test_stripe_wait_time(self):
		customer = baker.make(Customer)
		self.assertEqual(
			customer.stripe_wait_time(),
			int(PURCHASE_WAIT_TIME - customer.stripe_time_dif())
		)

	def test_stripe_enabled(self):
		customer = baker.make(Customer)
		self.assertEqual(
			customer.stripe_enabled(),
			customer.stripe_time_dif() > PURCHASE_WAIT_TIME
		)


class TestCardModel(TestCase):
	def test_foreign_key_relationship_with_customer(self):
		baker.make(Card)
		customer_total = Customer.objects.all().count()
		self.assertEqual(customer_total, 1)

	def test_str(self):
		card = baker.make(Card)
		test_string = f"{card.first_name} {card.last_name}: {card.src_id}"
		self.assertEqual(str(card), test_string)


class TestShippingAddressModel(TestCase):
	def test_foreign_key_relationship_customer(self):
		baker.make(ShippingAddress)
		customer_total = Customer.objects.all().count()
		self.assertEqual(customer_total, 1)

	def test_str(self):
		address = baker.make(ShippingAddress)
		test_str = f"{address.line1}, {address.city}, {address.state}, {address.zipcode}, {address.country}"
		self.assertEqual(str(address), test_str)


class TestItemModel(BaseItemTest):
	def test_foreign_key_relationship_with_item_category(self):
		baker.make(Item)
		total_item_category_count = ItemCategory.objects.all().count()

		self.assertEqual(total_item_category_count, 1)

	def test_str(self):
		item = baker.make(Item)
		test_str = f"{item.name} ({item.quantity} in stock)"

		self.assertEqual(str(item), test_str)

	def test_save_slugify(self):
		item = baker.make(Item)
		self.assertEqual(item.slug, slugify(item.name))

	def test_clean_fields_quantity(self):
		item = Item(quantity=-10)
		self.assertRaises(ValidationError, item.full_clean)

	def test_in_stock(self):
		item = baker.make(Item, quantity=10)
		self.assertEqual(item.in_stock(), True)

	def test_get_total_sold(self):
		order_item = self.order_item_ordered()
		item = order_item.item

		self.assertEqual(item.get_total_sold(), order_item.quantity)

	def test_get_total_earnings(self):
		order_item = self.order_item_ordered()
		item = order_item.item
		test_total = order_item.quantity * item.price
		
		self.assertEqual(item.get_total_earnings(), test_total)

	def test_get_rate(self):
		item_category = self.default_item_category()
		order_item = self.order_item_ordered()

		item = order_item.item
		item.item_category = item_category
		item.save()

		time_rate = 1  #daily rate
		total_days = (timezone.now() - item_category.date_started).days
		total_earnings = item.get_total_earnings()

		test_rate = round((total_earnings / total_days) * time_rate, 2)

		self.assertEqual(item.get_rate(time_rate), test_rate)

	def test_check_item_weekly_earnings_value_after_calling_function_record_stats(self):
		order_item = self.order_item_ordered()
		item = order_item.item
		item.record_stats()

		self.assertEqual(item.weekly_earnings, item.get_rate(7))


class TestItemCategoryModel(BaseItemTest):
	def test_str(self):
		item_category = baker.make(ItemCategory)
		self.assertEqual(str(item_category), item_category.name)

	def test_save_slugify(self):
		item_category = baker.make(ItemCategory)
		self.assertEqual(item_category.slug, slugify(item_category.name))

	def test_get_time_since_started_days(self):
		item_category = self.default_item_category()
		test_days = (timezone.now() - item_category.date_started).days

		self.assertEqual(item_category.get_time_since_started()[0], test_days)

	def test_record_stats(self):
		item_category = self.default_item_category()

		test_total_weekly = 0
		for i in range(0, 5):
			item = self.order_item_ordered().item
			item.item_category = item_category
			item.save()
			item.record_stats()

			test_total_weekly += item.weekly_earnings

		item_category.record_stats()

		self.assertEqual(item_category.weekly_earnings, test_total_weekly)

	def test_filter_category_link(self):
		filter_category = baker.make(FilterCategory)
		item_category = filter_category.item_category

		self.assertIn(filter_category.name, item_category.filter_category_link())


class TestFilterCategoryModel(TestCase):
	def test_foreign_key_relationship_with_item_category(self):
		baker.make(FilterCategory)
		item_category_count = ItemCategory.objects.all().count()

		self.assertEqual(item_category_count, 1)

	def test_str(self):
		filter_category = baker.make(FilterCategory)
		test_str = f"{filter_category.item_category.name}: {filter_category.name}"

		self.assertEqual(str(filter_category), test_str)

	def test_item_category_link(self):
		filter_category = baker.make(FilterCategory)
		self.assertIn(filter_category.item_category.name, filter_category.item_category_link())


class TestFilterOptionModel(TestCase):
	def test_foreign_key_relationship_with_filter_category(self):
		baker.make(FilterOption)
		filter_category_count = FilterCategory.objects.all().count()
		
		self.assertEqual(filter_category_count, 1)

	def test_str(self):
		filter_option = baker.make(FilterOption)
		test_str = f"{filter_option.filter_category.name}: {filter_option.name}"

		self.assertEqual(str(filter_option), test_str)


class TestOrderItemModel(BaseItemTest):
	def test_foreign_key_relationship_customer(self):		
		self.order_item_ordered()
		customer_total = Customer.objects.all().count()

		self.assertEqual(customer_total, 1)

	def test_foreign_key_relationship_order(self):
		self.order_item_ordered()
		order_total = Order.objects.all().count()

		self.assertEqual(order_total, 1)

	def test_str(self):
		order_item = baker.make(OrderItem)
		test_str = f"{order_item.quantity} of {order_item.item.name}"

		self.assertEqual(str(order_item), test_str)

	def test_get_price_total(self):
		order_item = self.order_item_ordered()
		test_total = order_item.quantity * order_item.item.price

		self.assertEqual(order_item.get_price_total(), test_total)

	def test_handle_quantity(self):
		order_item = self.order_item_in_cart()
		user_quantity = order_item.quantity - 1
		order_item.handle_quantity(user_quantity)

		self.assertEqual(order_item.quantity, user_quantity)

	def test_remove_from_cart(self):
		order_item = self.order_item_ordered()
		order_item.remove_from_cart()

		self.assertEqual(order_item.in_cart, False)


class TestOrderModel(BaseItemTest):
	def test_foreign_key_relationship_with_customer(self):
		baker.make(Order)
		customer_total = Customer.objects.all().count()

		self.assertEqual(customer_total, 1)

	def test_foreign_key_relationship_with_address(self):
		address = baker.make(ShippingAddress)
		baker.make(Order, shipping_address=address)
		address_total = ShippingAddress.objects.all().count()

		self.assertEqual(address_total, 1)

	def test_foreign_key_relationship_with_card(self):
		card = baker.make(Card)
		baker.make(Order, card=card)
		card_total = Card.objects.all().count()

		self.assertEqual(card_total, 1)

	def test_foreign_key_relationship_with_order_item(self):
		self.order_item_ordered()
		order_total = Order.objects.all().count()

		self.assertEqual(order_total, 1)

	def test_str(self):
		order = baker.make(Order)
		test_str = f"Order of {order.full_name}"

		self.assertEqual(str(order), test_str)

	def test_get_price_total_in_cart(self):
		order = self.order_with_order_items_in_cart()

		test_total = 0
		for order_item in order.orderitem_set.filter(in_cart=True, ordered=False):
			test_total += order_item.get_price_total()

		self.assertEqual(order.get_price_total(), test_total)

	def test_get_price_total_in_cart_and_ordered(self):
		order = self.order_with_order_items_ordered()

		test_total = 0
		for order_item in order.orderitem_set.filter(in_cart=True, ordered=True):
			test_total += order_item.get_price_total()

		self.assertEqual(order.get_price_total(), test_total)

	def test_get_order_description_str(self):
		order_item = self.order_item_ordered()
		item = order_item.item
		order = order_item.order

		order_description_str = order.get_order_description()[1]
		test_str = f"{order_item.quantity} order(s) of {item.name}: ${float(item.price)}"

		self.assertEqual(order_description_str, test_str)

	def test_record_payment(self):
		order_item = self.order_item_ordered()
		order_item.ordered = False
		order_item.save()

		order = order_item.order

		address = baker.make(ShippingAddress, customer=order.customer)
		card = baker.make(Card, customer=order.customer)
		payment_intent_id = 12345

		order.record_payment(card, address, payment_intent_id)

		self.assertTrue(order.ordered)
		self.assertEqual(order.card, card)
		self.assertEqual(order.shipping_address, address)
		self.assertEqual(order.payment_intent_id, payment_intent_id)
		self.assertEqual(order.email, address.email)
		self.assertIsNot(order.ref_code, None)