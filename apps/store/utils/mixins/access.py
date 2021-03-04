from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from store.models import Order
from store.utils.helper_functions.stripe import stripe_error
from store.utils.helper_functions.views import get_customer, get_billing_forms

from user_profile.utils.mixins.access import CustomTestMixin, LoginAccessMixin


class ItemListAccessMixin(CustomTestMixin):
	def get_base_test(self):
		self.url = reverse('store:item_category_list')
		return self.item_category.is_active


class ItemDetailAccessMixin(ItemListAccessMixin):
	def test_func(self):
		slug = self.item_category.slug		
		self.url = reverse('store:item_list', args=(slug,))
		return self.item.is_active


class CustomerAccessMixin(LoginAccessMixin):
	def test_func(self):
		self.customer = self.request.user.customer
		return True


class CheckoutAccessMixin(UserPassesTestMixin):
	def test_func(self):
		order_qs = Order.objects.filter(customer=self.customer, ordered=False)
		if order_qs.exists():
			order_items_qs = order_qs[0].orderitem_set.filter(in_cart=True, ordered=False)
			if order_items_qs.count() > 0:
				self.order = order_qs[0]
				return True

		return False

	def handle_no_permission(self):
		return redirect('store:item_category_list')


class CardAccessMixin(CustomerAccessMixin):
	def test_func(self):
		super().test_func()

		try:
			forms = get_billing_forms(self.customer)
			self.billing_forms = forms
			return True
		except:
			self.url = reverse('store:billing_profile')
			stripe_error(self.request)
			return False