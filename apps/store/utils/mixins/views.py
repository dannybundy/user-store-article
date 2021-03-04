from django.contrib import messages
from django.shortcuts import render, redirect
from store.utils.helper_functions.views import add, update, remove


def display_cart_msg(request, val):
	msg_success = val[0]
	msg = val[1]

	if msg_success:
		messages.success(request, msg)
	else:
		messages.warning(request, msg)


class CartMixin:
	def post(self, *args, **kwargs):
		self.cart_decision = self.request.POST['cart_decision'].lower()

		if 'remove' in self.cart_decision:
			val = remove(self.order_item)
			display_cart_msg(self.request, val)
			return redirect(self.get_success_url())

		return super().post(*args, **kwargs)

	def form_valid(self, form):
		user_quantity = int(self.request.POST['quantity'])
		if 'add' in self.cart_decision:
			val = add(self.order_item, user_quantity)

		elif 'update' in self.cart_decision:
			val = update(self.order_item, user_quantity)

		display_cart_msg(self.request, val)
		return super().form_valid(form)

	def get_success_url(self):
		return self.request.path_info


class CustomerFormArgMixin:
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs.update({'customer': self.customer})
		return kwargs
