from ckeditor.fields import RichTextField
from cloudinary.models import CloudinaryField

from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone


class Category(models.Model):
	name = models.CharField(max_length=30)
	slug = models.SlugField(unique=True, blank=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.name}"

	def save(self, *args, **kwargs):
		self.slug = self.slug or slugify(self.name)
		super().save(*args, **kwargs)


class Article(models.Model):
	category = models.ForeignKey(
		Category,
		on_delete=models.PROTECT,
	)

	title = models.CharField(max_length=50)
	description = models.CharField(max_length=100)
	body = RichTextField()
	image = CloudinaryField(blank=True, null=True)
	author = models.CharField(max_length=50)
	date_pub = models.DateTimeField(default=timezone.now)
	slug = models.SlugField(unique=True, blank=True)
	is_active = models.BooleanField(default=True)

	def __str__(self):
		return f"{self.title}: {self.description}"

	def save(self, *args, **kwargs):
		self.slug = self.slug or slugify(self.title)
		super().save(*args, **kwargs)