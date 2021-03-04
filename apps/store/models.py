from cloudinary.models import CloudinaryField
from dateutil.relativedelta import relativedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.template.defaultfilters import slugify
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html

from django_countries.fields import CountryField
from math import floor

from .utils.helper_functions.models import *


PURCHASE_WAIT_TIME = 5


class Customer(models.Model):
	user = models.OneToOneField(
		User, related_name='customer', on_delete=models.CASCADE, blank=True, null=True
	)

	full_name = models.CharField(max_length=100, default="Guest")
	email = models.EmailField(max_length=50, blank=True, null=True)
	stripe_customer_id = models.CharField(max_length=100, blank=True, null=True)

	purchase_attempt_time = models.DateTimeField(default=timezone.now)
	guest_num = models.IntegerField(default=0, blank=True, null=True)

	def __str__(self):
		return f"{self.full_name}"

	def save(self, *args, **kwargs):
		if self.user is not None:
			self.full_name = f"{self.user.first_name} {self.user.last_name}"
			self.email = self.user.email
			self.guest_num = None

		super().save(*args, **kwargs)
		return self

	def stripe_time_dif(self):
		return (timezone.now()-self.purchase_attempt_time).total_seconds()

	def stripe_wait_time(self):
		return int(PURCHASE_WAIT_TIME - self.stripe_time_dif())

	def stripe_enabled(self):
		return self.stripe_time_dif() > PURCHASE_WAIT_TIME


class Card(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
	src_id = models.CharField(max_length=30)

	line1 = models.CharField(max_length=30)
	line2 = models.CharField(max_length=30, blank=True, null=True)
	city = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	zipcode = models.CharField(max_length=20)
	country = CountryField(multiple=False)

	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	email = models.EmailField(max_length=30)

	def __str__(self):
		return f"{self.first_name} {self.last_name}: {self.src_id}"


class ShippingAddress(models.Model):
	customer = models.ForeignKey(Customer, on_delete=models.CASCADE)

	line1 = models.CharField(max_length=30)
	line2 = models.CharField(max_length=30, blank=True, null=True)
	city = models.CharField(max_length=30)
	state = models.CharField(max_length=30)
	zipcode = models.CharField(max_length=30)
	country = CountryField(multiple=False)

	first_name = models.CharField(max_length=30)
	last_name = models.CharField(max_length=30)
	email = models.EmailField(max_length=30)

	def __str__(self):
		if self.line2:
			address = f"{self.line1}, {self.line2}, {self.city}, {self.state}, {self.zipcode}, {self.country}"
		else:
			address = f"{self.line1}, {self.city}, {self.state}, {self.zipcode}, {self.country}"

		return address


class ItemCategory(models.Model):
	name = models.CharField(max_length=30, unique=True)
	slug = models.SlugField(unique=True, blank=True)
	date_started = models.DateTimeField(default=timezone.now)
	is_active = models.BooleanField(default=True)

	total_earnings = models.IntegerField(default=0)
	daily_earnings = models.IntegerField(default=0)
	weekly_earnings = models.IntegerField(default=0)
	monthly_earnings = models.IntegerField(default=0)
	yearly_earnings = models.IntegerField(default=0)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.inital_name = self.name

	def __str__(self):
		return f"{self.name}"

	def save(self, *args, **kwargs):
		self.slug = slugify(self.name)
		super().save(*args, **kwargs)

	def get_time_since_started(self):
		total_time = timezone.now() - self.date_started
		
		days = total_time.days
		weeks = floor(days / 7)
		months = floor(days / 31)
		years = floor(days / 365)

		total_time_str = f"""
			Store open for: {years} years,
			{months} months, {days} days
			"""
		return [days, total_time_str]

	def record_stats(self):
		total_earnings = 0
		daily_earnings = 0
		weekly_earnings = 0
		monthly_earnings = 0
		yearly_earnings = 0

		for item in Item.objects.filter(item_category=self):
			total_earnings += item.total_earnings
			daily_earnings += item.daily_earnings
			weekly_earnings += item.weekly_earnings
			monthly_earnings += item.monthly_earnings
			yearly_earnings += item.yearly_earnings

		self.total_earnings = total_earnings
		self.daily_earnings = daily_earnings
		self.weekly_earnings = weekly_earnings
		self.monthly_earnings = monthly_earnings
		self.yearly_earnings = yearly_earnings

		self.save()

	def filter_category_link(self):
		if self.pk:
		
			html_content = ''
			for filter_category in self.filtercategory_set.all():
				url = reverse('admin:store_filtercategory_change', args=(filter_category.pk,))
				html_content += '<a href="{}">{}</a><br>'.format(url, filter_category.name)

			add_url = reverse('admin:store_filtercategory_add')
			html_content += '<br><b><a href="%s">Add New Category</a></b>' % add_url

			return format_html(html_content)

		return ''

	filter_category_link.short_description = "Filter Categories"


class FilterCategory(models.Model):
	item_category = models.ForeignKey(
		ItemCategory,
		on_delete=models.CASCADE
	)
	name = models.CharField(max_length=30, unique=True)

	def __str__(self):
		return f"{self.item_category}: {self.name}"

	def item_category_link(self):
		if self.pk:
			url = reverse('admin:store_itemcategory_change', args=(self.item_category.pk,))
			html_content = '<br><b><a href="{}">Go back to {}</a></b>'.format(url, self.item_category.name)

			return format_html(html_content)

		return ''

	item_category_link.short_description = ""


class FilterOption(models.Model):
	filter_category = models.ForeignKey(
		FilterCategory,
		on_delete=models.CASCADE
	)
	name = models.CharField(max_length=30, unique=True)

	def __str__(self):
		return f"{self.filter_category.name}: {self.name}"



class Item(models.Model):
	item_category = models.ForeignKey(
		ItemCategory,
		on_delete=models.CASCADE
		)
	filter_option = models.ManyToManyField(FilterOption, blank=True)

	name = models.CharField(max_length=50, unique=True)
	description = models.TextField()
	price = models.FloatField(default=0)
	discount_price = models.FloatField(blank=True, null=True)
	quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
	image = CloudinaryField(blank=True, null=True)
	slug = models.SlugField(blank=True, null=True, unique=True)
	is_active = models.BooleanField(default=True)

	total_sold = models.IntegerField(default=0)
	total_earnings = models.IntegerField(default=0)
	daily_earnings = models.IntegerField(default=0)
	weekly_earnings = models.IntegerField(default=0)
	monthly_earnings = models.IntegerField(default=0)
	yearly_earnings = models.IntegerField(default=0)	

	def __str__(self):
		return f"{self.name} ({self.quantity} in stock)"

	def save(self, *args, **kwargs):
		self.slug = self.slug or slugify(self.name)
		super().save(*args, **kwargs)

		return self

	def clean_fields(self, exclude=None):
		if self.quantity < 0:
			raise ValidationError({'quantity': "Quantity can't be negative."})

	def in_stock(self):
		if self.quantity > 0:
			return True

		return False

	def get_total_sold(self):
		quantity = 0
		for order_item in self.orderitem_set.filter(ordered=True, in_cart=True):
			quantity += order_item.quantity

		return quantity

	def get_total_earnings(self):
		total_earnings = 0
		for order_item in self.orderitem_set.filter(ordered=True, in_cart=True):
			total_earnings += order_item.get_price_total()

		return total_earnings

	def get_rate(self, time_rate):
		total_days = self.item_category.get_time_since_started()[0]
		if total_days == 0:
			total_days = 1

		rate = round((self.get_total_earnings() / total_days) * time_rate, 2)
		
		return rate

	def record_stats(self):
		self.total_sold = self.get_total_sold()
		self.total_earnings = self.get_total_earnings() 
		self.daily_earnings = self.get_rate(1)
		self.weekly_earnings = self.get_rate(7)
		self.monthly_earnings = self.get_rate(31)
		self.yearly_earnings = self.get_rate(365)
		self.save()


class Order(models.Model):
	customer = models.ForeignKey(
		Customer,
		on_delete=models.CASCADE,
	)
	shipping_address = models.ForeignKey(
		ShippingAddress,
		on_delete=models.CASCADE,
		blank=True,
		null=True
	)
	card = models.ForeignKey(
		Card,
		on_delete=models.CASCADE,
		blank=True,
		null=True
	)

	full_name = models.CharField(max_length=100, blank=True, null=True)
	email = models.CharField(max_length=30, blank=True, null=True)

	payment_intent_id = models.CharField(max_length=30, blank=True, null=True)
	ref_code = models.CharField(max_length=20, blank=True, null=True)
	date = models.DateTimeField(blank=True, null=True)

	ordered = models.BooleanField(default=False)
	delivered = models.BooleanField(default=False)
	recieved = models.BooleanField(default=False)
	refund_requested = models.BooleanField(default=False)
	refund_granted = models.BooleanField(default=False)
	cancelled = models.BooleanField(default=False)

	def __str__(self):
		string = ''
		if self.cancelled:
			string = ' (cancelled)'

		return f"Order of {self.full_name}{string}"

	def save(self, *args, **kwargs):
		self.full_name = self.customer.full_name
		super().save(*args, **kwargs)

		return self

	def get_price_total(self):
		price_total = 0
		for order_item in self.orderitem_set.all():
			price_total += order_item.get_price_total()

		return price_total

	def get_order_description(self):
		description_list = []
		for order_item in self.orderitem_set.all():
			item = order_item.item
			description_list.append(
				f"{order_item.quantity} order(s) of {item.name}: ${item.price}"
			)

		description_str = ', '.join(description_list)

		return [description_list, description_str] 

	def record_payment(self, card, shipping_address, payment_intent_id):
		item_category_list = []
		for order_item in self.orderitem_set.filter(in_cart=True, ordered=False):
			order_item.ordered = True
			order_item.save()

			item = order_item.item
			item.record_stats()
			item_category_list.append(item.item_category)
			item_category_list = list(set(item_category_list))

		for item_category in item_category_list:
			item_category.record_stats()
		
		self.shipping_address = shipping_address
		self.card = card
		self.email = shipping_address.email

		self.payment_intent_id = payment_intent_id
		self.ref_code = create_ref_code()
		self.ordered = True
		self.date = timezone.now()

		self.save()

		if self.customer.guest_num is not None:
			self.customer.full_name = f"{card.first_name} {card.last_name}"
			self.customer.email = card.email
			self.customer.save()


class OrderItem(models.Model):
	customer = models.ForeignKey(
		Customer,
		on_delete=models.CASCADE
	)
	order = models.ForeignKey(Order, on_delete=models.CASCADE)
	item = models.ForeignKey(Item, on_delete=models.CASCADE)	

	quantity = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1)])
	in_cart = models.BooleanField(default=False)
	ordered = models.BooleanField(default=False)

	def __str__(self):
		return f"{self.quantity} of {self.item.name}"

	def clean_fields(self, exclude=None):
		if self.quantity < 0:
			raise ValidationError({'quantity': "Quantity cannot be negative."})

	def get_price_total(self):
		return self.quantity * self.item.price

	def handle_quantity(self, user_quantity):
		valid_quantity = None
		item = self.item

		# Positive = removing from order
		# Negative = adding to order
		quantity_dif = self.quantity - user_quantity

		# Can't add, none in stock
		if quantity_dif < 0 and not item.in_stock():
			return valid_quantity

		# Not enough in stock to completely add but adds the rest of the item quantity
		# to the order item
		elif quantity_dif < 0 and abs(quantity_dif) > item.quantity:
			self.quantity += item.quantity
			item.quantity = 0
			valid_quantity = False

		# There is enough in stock
		else:
			self.quantity -= quantity_dif
			item.quantity += quantity_dif
			valid_quantity = True

		self.in_cart = True

		self.save()
		item.save()

		return valid_quantity

	def remove_from_cart(self):
		self.item.quantity += self.quantity
		self.item.save()

		self.quantity = 0
		self.in_cart = False
		self.save()

		return self.quantity




def customer_reciever(sender, instance, created, *args, **kwargs):
	if created:
		customer = Customer.objects.create(
			user=instance,
		)
post_save.connect(customer_reciever, sender=User)