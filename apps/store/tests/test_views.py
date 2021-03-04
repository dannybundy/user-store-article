from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from model_bakery import baker
import datetime

from store.models import *
from store.utils.helper_functions.views import get_customer

from .utils.helper_functions import *


class TestItemCategoryList(TestCase):
	def test_item_category_list(self):
		item_category = baker.make(ItemCategory)
		url = reverse('store:item_category_list')
		
		response = self.client.get(url)
		qs_list = response.context['itemcategory_list']
		
		self.assertIs(len(qs_list), 1)
		self.assertContains(response, item_category.name)


class TestItemListView(BaseItemTest):
	def test_redirect_to_item_category_list_if_item_category_is_not_active(self):
		item_category = baker.make(ItemCategory, is_active=False)
		slug = item_category.slug
		url = reverse('store:item_list', args=(slug,))

		response = self.client.get(url)
		test_redirect_url = reverse('store:item_category_list')

		self.assertRedirects(response, test_redirect_url)

	def test_get_chosen_filters(self):
		val = self.items_with_filter_options()
		item_category = val[0]
		filter_option = val[1]

		slug = item_category.slug
		url = reverse('store:item_list', args=(slug,))

		pk = filter_option.pk
		data = {'filter_applied': True, 'filter_option': [str(pk)]}
		response = self.client.get(url, data=data)
		
		test_item = Item.objects.filter(filter_option=filter_option)[0]
		test_html = "checked"

		self.assertEqual(response.context['chosen_filter_pk_list'], [pk])
		self.assertIn(test_item, response.context['item_list'])
		self.assertContains(response, "checked", 1)
		self.assertContains(response, test_item.name)


class TestSearchResultsView(TestCase):
	def test_item_in_qs_after_search(self):
		item = baker.make(Item)

		url = reverse('store:search_results')
		data = {'search_input': item.name}
		response = self.client.get(url, data)

		self.assertIn(item, response.context['item_list'])
		self.assertContains(response, item.name)



class TestItemDetailView(BaseItemTest):
	def set_view(self, item, customer=None, data=False):
		category_slug = item.item_category.slug
		item_slug = item.slug
		url = reverse('store:item_detail', args=(category_slug, item_slug))

		if data:
			session = self.client.session
			session['guest_num'] = customer.guest_num
			session.save()
			response = self.client.post(url, data=data)
		else:
			response = self.client.get(url)

		return response

	def test_redirect_to_item_list_if_item_category_is_active_but_item_is_not(self):
		item = baker.make(Item, is_active=False)
		response = self.set_view(item)
		test_url = reverse('store:item_list', args=(item.item_category.slug,))

		self.assertRedirects(response, test_url)

	def test_variable_add_added_to_context_data_if_item_is_not_in_cart(self):
		order_item = baker.make(OrderItem)
		item = order_item.item
		response = self.set_view(item)

		self.assertIn('add', response.context)
		self.assertNotIn('quantity', response.context)

	def test_post_request_add(self):
		order_item = self.default_order_item()
		item = order_item.item
		customer = order_item.customer

		user_quantity = order_item.quantity+1
		data = {
			'cart_decision': 'add',
			'quantity': user_quantity
		}

		response = self.set_view(item, customer, data)
		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertEqual(order_item.quantity, user_quantity)
		self.assertTrue(order_item.in_cart)

	def test_post_request_update(self):
		order_item = self.order_item_in_cart()
		item = order_item.item
		customer = order_item.customer

		user_quantity = order_item.quantity+1
		data = {
			'cart_decision': 'update',
			'quantity': user_quantity
		}

		response = self.set_view(item, customer, data)
		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertEqual(order_item.quantity, user_quantity)

	def test_post_request_remove(self):
		order_item = self.order_item_in_cart()
		item = order_item.item
		customer = order_item.customer

		user_quantity = order_item.quantity+1
		data = {'cart_decision': 'remove'}

		response = self.set_view(item, customer, data)
		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertFalse(order_item.in_cart)


class TestOrderSummaryView(BaseItemTest):
	def test_empty_cart(self):
		url = reverse('store:order_summary')
		response = self.client.get(url)

		self.assertContains(response, "Your cart is empty")

	def set_view(self, order_item, data=False):
		customer = order_item.customer
		order = order_item.order

		session = self.client.session
		session['guest_num'] = customer.guest_num
		session.save()

		url = reverse('store:order_summary')
		if data:
			response = self.client.post(url, data=data)
		else:
			response = self.client.get(url)

		return response

	def test_order_price_total(self):
		order_item = self.order_item_in_cart()
		response = self.set_view(order_item)

		self.assertContains(response, order_item.order.get_price_total())
		self.assertContains(response, order_item.get_price_total())

	def test_post_request_remove(self):
		order_item = self.order_item_in_cart()
		data = {
			'item': order_item.item.pk,
			'cart_decision': 'remove',
		}

		response = self.set_view(order_item, data)
		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertFalse(order_item.in_cart)

	def test_post_request_remove(self):
		order_item = self.order_item_in_cart()
		user_quantity = order_item.quantity+1
		data = {
			'item': order_item.item.pk,
			'cart_decision': 'update',
			'quantity': user_quantity
		}

		response = self.set_view(order_item, data)
		order_item = OrderItem.objects.get(pk=order_item.pk)

		self.assertEqual(order_item.quantity, user_quantity)



class CheckoutViewTest(TestCase):
	def test_redirect_if_no_items_in_order(self):
		order = baker.make(Order)

		url = reverse('store:checkout')
		response = self.client.get(url)
		test_url = reverse('store:item_category_list')

		self.assertRedirects(response, test_url)

	def test_if_stored_address_list_is_added_to_context_data_if_stored_address_exists(self):
		user = baker.make(User)
		customer = Customer.objects.get(user=user)
		address = baker.make(ShippingAddress, customer=customer)

		self.client.force_login(user=user)
		url = reverse('store:shipping_address')
		response = self.client.get(url)

		self.assertIn('stored_address_list', response.context)


class BillingProfileViewTest(TestCase):
	def test_redirect_if_not_logged_in(self):
		url = reverse('store:billing_profile')
		response = self.client.get(url)
		test_url = reverse('profile:login')

		self.assertRedirects(response, test_url)


# class CardViewTest(TestCase):
# 	def test_length_of_billing_form_list(self):
# 		user = baker.make(User)
# 		customer = Customer.objects.get(user=user)
# 		card = baker.make(Card, customer=customer)

# 		self.client.force_login(user=user)
# 		url = reverse('store:cards')
# 		response = self.client.get(url)

# 		billing_form_list = response.context['billing_form_list']

# 		self.assertEquals(len(billing_form_list), 1)


class AddressViewTest(TestCase):
	def test_length_of_address_form_list(self):
		user = baker.make(User)
		customer = Customer.objects.get(user=user)
		address = baker.make(ShippingAddress, customer=customer)

		self.client.force_login(user=user)
		url = reverse('store:shipping_address')
		response = self.client.get(url)

		address_form_list = response.context['address_form_list']

		self.assertEquals(len(address_form_list), 1)


class OrderHistoryViewTest(TestCase):
	def test_order_attributes_in_template(self):
		user = baker.make(User)
		customer = Customer.objects.get(user=user)
		order = baker.make(Order, customer=customer, ordered=True)
		order_item = baker.make(
			OrderItem,
			customer=customer,
			order=order,
			in_cart=True,
			ordered=True
		)

		self.client.force_login(user=user)

		url = reverse('store:order_history')
		response = self.client.get(url)

		self.assertContains(response, order.get_price_total())
		self.assertContains(response, order.shipping_address)