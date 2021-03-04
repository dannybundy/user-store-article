from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse

from user_profile.utils.mixins.access import CustomTestMixin


class ArticleListAccessMixin(CustomTestMixin):
	def get_base_test(self):
		self.url = reverse('article:category_list')
		return self.category.is_active


class ArticleDetailAccessMixin(ArticleListAccessMixin):
	def test_func(self):
		slug = self.category.slug
		article = self.get_object()		
		self.url = reverse('article:article_list', args=(slug,))
		
		return article.is_active