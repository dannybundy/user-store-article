import pytz
import django_tables2 as tables

from django.contrib import admin, messages
from django.contrib.admin.views.main import ChangeList
from django.db.models import Count, Sum, Avg, F, FloatField
from django.http import JsonResponse
from django.shortcuts import redirect

from dateutil.relativedelta import relativedelta
from dateutil import parser
from django_tables2 import RequestConfig
from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from store.models import *
from .forms import *
from .utils.actions import *
from .utils.helper_functions import *
from .utils.mixins import *


class CardInline(NoAddChangeDeleteMixin, admin.StackedInline):
	model = Card
	extra = 0


class ShippingAddressInline(NoAddChangeDeleteMixin, admin.StackedInline):
	model = ShippingAddress
	extra = 0


class CustomerAdmin(NoAddChangeDeleteMixin, admin.ModelAdmin):
	inlines = [CardInline, ShippingAddressInline]
	fields = ['user_or_guest', 'full_name', 'email', 'stripe_customer_id', 'purchase_attempt_time']
	list_display = ['user_or_guest', 'full_name', 'email', 'stripe_customer_id']
	search_fields = [
		'user__username', 'user__phonenumber',
		'full_name', 'email', 'stripe_customer_id',
	]

	def user_or_guest(self, obj):
		return get_user_or_guest(obj)

	def get_fields(self, request, obj=None):
		field = []
		if obj is not None:
			if obj.user is not None:
				field = ['user',]
			else:
				field = ['guest_num',]

		return field + self.fields


class ItemTable(tables.Table):
	class Meta:
		model = Item
		fields = [
			'name', 'price', 'total_sold', 'total_earnings',
			'daily_earnings', 'weekly_earnings', 'monthly_earnings',
			'yearly_earnings', 'item_category', 'item_category__total_earnings',
			'item_category__daily_earnings', 'item_category__weekly_earnings',
			'item_category__monthly_earnings', 'item_category__yearly_earnings'
		]


class ItemCategoryAdmin(NoDeleteMixin, admin.ModelAdmin):
	model = ItemCategory
	fields = ['name', 'filter_category_link', 'is_active']
	readonly_fields = [
		'slug', 'date_started', 'total_earnings', 'daily_earnings',
		'weekly_earnings', 'monthly_earnings', 'yearly_earnings',
		'filter_category_link'
	]
	list_display = [
		'name', 'date_started', 'total_earnings', 'daily_earnings',
		'weekly_earnings', 'monthly_earnings', 'yearly_earnings'
	]

	def change_view(self, request, object_id, extra_context=None):
		extra_context = extra_context or {}
		extra_context = hide_admin_btns(extra_context)

		request.session['item_category_pk'] = object_id

		item_category = ItemCategory.objects.get(id=object_id)
		item_qs = Item.objects.filter(item_category__pk=item_category.pk)
		table = ItemTable(item_qs)

		RequestConfig(request).configure(table)

		extra_context['total_time'] = item_category.get_time_since_started()[1]

		if request.is_ajax():
			return JsonResponse({'table':table.as_html(request)}, status=200)
		else:
			extra_context['table'] = table

		return super().change_view(request, object_id, extra_context=extra_context)



class FilterOptionInline(admin.TabularInline):
	model = FilterOption
	extra = 0


class FilterCategoryAdmin(admin.ModelAdmin):
	inlines = [FilterOptionInline,]
	verbose_name_plural = 'Filter Category'
	fields = ['name', 'item_category_link']
	readonly_fields = ['item_category_link']

	def get_model_perms(self, request):
		return {}

	def get_parent_url(self, pk):
		item_category = FilterCategory.objects.get(pk=pk).item_category
		return reverse('admin:store_itemcategory_change', args=(item_category.pk,))

	def save_model(self, request, obj, form, change):
		if not change:
			pk = request.session.get('item_category_pk', None)
			if pk is not None:
				obj.item_category = ItemCategory.objects.get(pk=pk)
				request.session.pop('item_category_pk', None)

		return super().save_model(request, obj, form, change)

	def add_view(self, request, extra_context=None):
		extra_context = extra_context or {}
		extra_context = hide_admin_btns(extra_context)

		pk = request.session.get('item_category_pk', None)
		if pk is None:
			return redirect('admin:store_itemcategory_changelist')

		return super().add_view(request, extra_context=extra_context)

	def response_add(self, request, obj, post_url_continue=None):
		return redirect(self.get_parent_url(obj.pk))

	def change_view(self, request, object_id, extra_context=None):
		extra_context = extra_context or {}
		extra_context = hide_admin_btns(extra_context)

		pk = request.session.get('item_category_pk', None)
		if pk is None:
			return redirect('admin:store_itemcategory_changelist')

		return super().change_view(request, object_id, extra_context=extra_context)

	def response_change(self, request, obj):
		return redirect(request.get_full_path())

	def response_delete(self, request, obj, post_url_continue=None):
		pk = request.session['item_category_pk']
		request.session.pop('item_category_pk', None)
		return redirect(self.get_parent_url(pk))


class ItemAdmin(admin.ModelAdmin):
	readonly_fields = [
		'slug', 'total_sold', 'total_earnings', 'daily_earnings',
		'weekly_earnings', 'monthly_earnings', 'yearly_earnings'
	]
	list_display = [
		'name', 'item_price', 'discount_price',
		'quantity', 'is_active'
	]
	search_fields = [
		'name', 'price', 'quantity', 'filter_option__name',
		'filter_option__category__name'
	]
	actions = [make_active, make_inactive]

	def item_price(self, obj):
		return f"${obj.price}"


class OrderItemInline(NoAddChangeDeleteMixin, admin.TabularInline):
	model = OrderItem
	verbose_name = 'Item'
	extra = 0
	fields = ['item', 'quantity', 'in_cart', 'ordered']
	readonly_fields = ['item', 'quantity', 'in_cart', 'ordered']


class OrderAdmin(NoAddDeleteMixin, admin.ModelAdmin):
	inlines = [OrderItemInline,]
	fields = [
		'customer', 'full_name', 'email', 'payment_intent_id',
		'card', 'ref_code', 'date', 'ordered', 'delivered',
		'recieved', 'refund_requested', 'refund_granted',
		'cancelled'
	]
	readonly_fields = [
		'customer', 'full_name', 'email', 'payment_intent_id',
		'card', 'ref_code', 'date'
	]
	list_display = [
		'user_or_guest', 'full_name', 'order_total', 'ref_code', 'ordered',
		'delivered', 'recieved', 'refund_requested',
		'refund_granted', 'cancelled'
	]
	list_editable = ['delivered', 'recieved']
	actions = [
		delivered, undelivered,
		recieved, unrecieved,
		refund, unrefund,
		cancel, uncancel
	]
	list_filter = [
		['date', DateRangeFilter],
		'orderitem__item__item_category',
		'orderitem__item__filter_option'
	]
	search_fields = [
		'full_name', 'email', 'payment_intent_id',
		'ref_code', 'orderitem__item__name'
	]

	def user_or_guest(self, obj):
		return get_user_or_guest(obj)

	def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
		field = super().formfield_for_foreignkey(db_field, request, **kwargs)
		pk = request.resolver_match.kwargs.get('object_id', None)
		if pk is not None:
			customer = Order.objects.get(pk=pk).customer
		
			if db_field.name == 'shipping_address':
				field.queryset = field.queryset.filter(customer=customer)

		return field

	def order_total(self, obj):
		return f"${obj.get_price_total()}"




admin.site.register(Customer, CustomerAdmin)
# admin.site.register(Card)
# admin.site.register(ShippingAddress)
admin.site.register(Item, ItemAdmin)
admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem)
# admin.site.register(Order)
admin.site.register(FilterCategory, FilterCategoryAdmin)
admin.site.register(ItemCategory, ItemCategoryAdmin)