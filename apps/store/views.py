from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
	DetailView,
	FormView,
	ListView,
	TemplateView,
	View
)

from user_profile.forms import PasswordValidationForm
from user_profile.models import UserProfile
from user_profile.utils.mixins.access import LoginAccessMixin
from user_profile.utils.mixins.views import RequestFormMixin, VerifyPasswordContextMixin

from .forms import *
from .models import *
from .utils.filters import *
from .utils.helper_functions.stripe import PUB_KEY, stripe_delete_card
from .utils.helper_functions.views import *
from .utils.mixins.access import *
from .utils.mixins.views import *


class ItemCategoryListView(ListView):
	model = ItemCategory
	template_name = 'store/item_category_list.html'
	queryset = ItemCategory.objects.filter(is_active=True).order_by('name')


class ItemListView(ItemListAccessMixin, ListView):
	model = Item
	slug_field = 'slug'
	slug_url_kwarg = 'item_category'
	paginate_by = 10
	template_name = 'store/item_list.html'

	item_category = None
	chosen_filters = []

	def setup(self, request, *args, **kwargs):
		self.item_category = ItemCategory.objects.get(slug=kwargs['item_category'])
		self.chosen_filters = get_chosen_filters(request)
		return super().setup(request, *args, **kwargs)

	def get_queryset(self):
		item_list = Item.objects.filter(item_category=self.item_category, is_active=True)
		item_list = filter_item_list(
			self.item_category,
			item_list,
			self.chosen_filters
		).order_by('name')

		return item_list

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['item_category'] = self.item_category
		context['chosen_filter_pk_list'] = self.chosen_filters

		return context


class SearchResultsView(ListView):
	model = Item
	paginate_by = 1
	template_name = "store/search_results.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['query'] = self.request.session.get('query', '')
		return context

	def get_queryset(self):
		if self.request.method == 'GET':
			query = self.request.GET.get('search_input')
			if query is None:
				query = self.request.session.get('query', '')

			result = Item.objects.filter(Q(name__icontains=query))
			self.request.session['query'] = query
			return result.order_by('name')

		return Item.objects.all().order_by('name')


class ItemDetailView(ItemDetailAccessMixin, CartMixin, FormView):
	form_class = QuantityForm
	template_name = 'store/item_detail.html'

	customer = None
	item_category = None
	item = None
	order = None
	order_item = None

	def set_variables(self, request, kwargs):
		self.customer = get_customer(request)
		self.item_category = ItemCategory.objects.get(slug=kwargs['item_category'])
		self.item = Item.objects.get(slug=kwargs['item'])

		self.order = Order.objects.get_or_create(
			customer=self.customer,
			ordered=False
		)[0]
		
		self.order_item = OrderItem.objects.get_or_create(
			customer=self.customer,
			order=self.order,
			item=self.item,
			ordered=False
		)[0]

	def setup(self, request, *args, **kwargs):
		self.set_variables(request, kwargs)
		return super().setup(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		order_item_qs = self.order.orderitem_set.filter(item=self.item, in_cart=True)
		if not order_item_qs.exists():
			context['add'] = True
			quantity = 1
		else:
			quantity = order_item_qs[0].quantity
			context['quantity'] = quantity

		context['item'] = self.item
		context['form'].fields['quantity'].initial = quantity

		return context


class OrderSummaryView(CartMixin, FormView):
	form_class = QuantityForm
	template_name = 'store/order_summary.html'

	customer = None
	order = None
	order_item = None
	order_item_list = None

	def set_variables(self, request, kwargs):
		self.customer = get_customer(request)
		
		order_qs = Order.objects.filter(
			customer=self.customer,
			ordered=False
		)
		if order_qs.exists():
			self.order = order_qs[0]
			self.order_item_list = self.order.orderitem_set.filter(
				ordered=False,
				in_cart=True
			)

	def setup(self, request, *args, **kwargs):
		self.set_variables(request, kwargs)
		return super().setup(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['order'] = self.order
		context['order_item_list'] = self.order_item_list

		return context

	def set_order_item(self, item):
		self.order_item = OrderItem.objects.get(
			customer=self.customer,
			item=item,
			in_cart=True,
			ordered=False,
		)

	def post(self, *args, **kwargs):
		pk = self.request.POST['item']
		item = Item.objects.get(pk=pk)
		self.set_order_item(item)
		return super().post(*args, **kwargs)


class CheckoutView(CheckoutAccessMixin, TemplateView):
	template_name = 'store/checkout.html'
	customer = None
	order = None

	def setup(self, request, *args, **kwargs):
		self.customer = get_customer(request)
		return super().setup(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['PUB_KEY'] = PUB_KEY
		context['shipping_form'] = ShippingAddressForm(self.customer)
		context['billing_form'] = BillingAddressForm(self.customer)

		context['stored_address_list'] = StoredAddressForm(self.customer)
		context['stored_card_list'] = StoredCardForm(self.customer)

		return context

	def post(self, *args, **kwargs):
		if self.customer.stripe_enabled():
			self.customer.purchase_attempt_time = timezone.now()
			self.customer.save()
			
			form = ShippingAddressForm(self.customer, self.request.POST)
			if form.is_valid():
				address = form.save()
			else:
				pk = self.request.POST.get('stored_address')
				if pk:
					address = ShippingAddress.objects.get(pk=pk)
				else:
					address = None
					messages.warning(self.request, "You did not choose a shipping address.")


			form = BillingAddressForm(self.customer, self.request.POST)
			if form.is_valid():
				try:
					stripe_src = self.request.POST['stripeToken']
					card = form.save(stripe_src)
				except:
					stripe_error(self.request)
					return redirect(self.request.path_info)
			else:
				pk = self.request.POST.get('stored_card')
				if pk:
					card = Card.objects.get(pk=pk)
				else:
					card = None
					messages.warning(self.request, "You did not choose a payment method.")


			if address is None or card is None:
				return redirect('store:checkout')

			try:
				form.make_payment(self.order, card, address)
			except:
				stripe_error(self.request)
				return redirect(self.request.path_info)

			if self.request.user.is_authenticated:
				url = reverse('store:order_history')
				messages.success(
					self.request,
					f"""Order went through! Order information is in
					<a href='{url}'>Order History</a> and has been sent
					to your email.
					"""
				)
			else:
				messages.success(
					self.request,
					"Order went through! Order information has been sent to your email."
				)
		else:
			messages.warning(
				self.request,
				f"""Wait {int(self.customer.stripe_wait_time())} seconds before
				processing another order.
				"""
			)

		return redirect('store:item_category_list')


class BillingProfileView(LoginAccessMixin, VerifyPasswordContextMixin, TemplateView):
	template_name = "store/billing_profile.html"


class CardView(CardAccessMixin,
				SuccessMessageMixin,
				VerifyPasswordContextMixin,
				CustomerFormArgMixin,
				FormView):
	form_class = BillingAddressForm
	template_name = "store/cards.html"
	success_url = reverse_lazy('store:card')
	success_message = None

	card = None
	billing_forms = None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['PUB_KEY'] = PUB_KEY
		context['billing_form_list'] = self.billing_forms
		context['stored_card_list'] = StoredCardForm(self.customer)

		return context

	def post(self, *args, **kwargs):
		pk = self.request.POST.get('pk')
		if pk is not None:
			self.card = Card.objects.get(pk=pk)

		delete = self.request.POST.get('delete')
		if delete is not None:
			try:
				stripe_delete_card(self.customer, self.card)
			except:
				stripe_error(request)
				return redirect('store:billing_profile')

			self.card.delete()
			messages.success(self.request, "Card has been deleted.")
			return redirect(self.request.path_info)

		return super().post(*args, **kwargs)

	def form_valid(self, form):
		if self.customer.stripe_enabled():
			try:
				add = self.request.POST.get('add')
				if add is not None:
					stripe_src = self.request.POST['stripeToken']
					form.save(stripe_src)
					self.success_message = "Card has been added."
				else:
					form.update(self.card)
					self.success_message = "Card has been updated."
			except:
				stripe_error(self.request)
				return redirect('store:billing_profile')
		else:
			messages.warning(
				self.request,
				f"""Wait {int(self.customer.stripe_wait_time())} seconds before
				processing another request.
				"""
			)	

		return super().form_valid(form)


class ShippingAddressView(CustomerAccessMixin,
							SuccessMessageMixin,
							VerifyPasswordContextMixin,
							CustomerFormArgMixin,
							FormView):
	form_class = ShippingAddressForm
	template_name = "store/shipping_address.html"
	success_url = reverse_lazy('store:shipping_address')
	success_message = None

	address = None

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		context['stored_address_list'] = StoredAddressForm(self.customer)
		context['address_form_list'] = get_address_forms(self.customer)
		return context

	def post(self, *args, **kwargs):
		pk = self.request.POST.get('pk')
		if pk is not None:
			self.address = ShippingAddress.objects.get(pk=pk)

		delete = self.request.POST.get('delete')
		if delete is not None:
			self.address.delete()
			messages.success(self.request, "Shipping Address has been deleted.")
			return redirect(self.request.path_info)

		return super().post(*args, **kwargs)

	def form_valid(self, form):
		add = self.request.POST.get('add')

		if add is not None:
			form.save()
			self.success_message = "Shipping Address has been added."
		else:
			form.update(self.address)
			self.success_message = "Shipping Address has been updated."

		return super().form_valid(form)


class OrderHistoryView(CustomerAccessMixin, VerifyPasswordContextMixin, TemplateView):
	template_name = "store/order_history.html"

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		order_list = Order.objects.filter(
			customer=self.customer,
			ordered=True,
		)
		context['order_list'] = order_list
		return context