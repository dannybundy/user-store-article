from django.template.defaultfilters import slugify
from django.test import TestCase

from model_bakery import baker

from article.models import *


class ArticleModelTest(TestCase):
	def test_foreign_key_relationship_with_category(self):
		article = baker.make(Article, body="body")
		self.assertEqual(Category.objects.all().count(), 1)

	def test_str(self):
		article = baker.make(Article, body="body")
		self.assertEqual(str(article), f"{article.title}: {article.description}")

	def test_model_save(self):
		article = baker.make(Article, body="body")
		self.assertEqual(article.slug, slugify(article.title))

class CategoryModelTest(TestCase):
	def test_str(self):
		category = baker.make(Category)
		self.assertEqual(str(category), category.name)