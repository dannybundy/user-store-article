from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from model_bakery import baker

from article.models import *


class TestCategoryListView(TestCase):
	def test_article_category_list(self):
		article = baker.make(Article, body="body")
		category = article.category

		url = reverse('article:category_list')
		response = self.client.get(url)
		
		self.assertIn(category, response.context['category_list'])
		self.assertContains(response, category.name)
		self.assertContains(response, article.title)


class TestArticleListView(TestCase):
	def test_redirect_to_category_list_if_article_category_is_not_active(self):
		article = baker.make(Article, body="body")
		category = article.category

		category.is_active = False
		category.save()

		url = reverse('article:article_list', args=(category.slug,))
		response = self.client.get(url)
		test_redirect_url = reverse('article:category_list')

		self.assertRedirects(response, test_redirect_url)


class TestArticleDetailView(TestCase):
	def test_redirect_to_article_list_if_category_is_active_but_article_is_not(self):
		article = baker.make(Article, body="body", is_active=False)
		category = article.category

		url = reverse(
			'article:article_detail',
			kwargs={'category': category.slug, 'article': article.slug}
		)
		response = self.client.get(url)
		test_url = reverse('article:article_list', args=(category.slug,))

		self.assertRedirects(response, test_url)

	def test_recent_articles_queryset_length(self):
		category = baker.make(Category)
		for i in range(10):
			article = baker.make(Article, category=category, body="body")

		category = article.category

		url = reverse(
			'article:article_detail',
			kwargs={'category': category.slug, 'article': article.slug}
		)
		response = self.client.get(url)

		self.assertIs(len(response.context['article_list']), 3)


class TestSearchResultsView(TestCase):
	def test_article_in_qs_after_search(self):
		article = baker.make(Article, body="body")

		url = reverse('article:search_results')
		data = {'search_input': article.title}
		response = self.client.get(url, data)

		self.assertIn(article, response.context['article_list'])
		self.assertContains(response, article.title)