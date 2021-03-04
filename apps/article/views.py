import datetime

from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.views.generic import (
	DetailView,
	FormView,
	ListView,
	TemplateView,
	UpdateView,
	View
)

from .models import *
from .utils.mixins.access import *


class CategoryListView(ListView):
	model = Category
	queryset = Category.objects.order_by('name')
	template_name = "article/category_list.html"


class ArticleListView(ArticleListAccessMixin, ListView):
	model = Article
	template_name = "article/article_list.html"

	def setup(self, request, *args, **kwargs):
		self.category = Category.objects.get(slug=kwargs['category'])
		return super().setup(request, *args, **kwargs)

	def get_queryset(self):
		qs = Article.objects.filter(category__slug=self.category.slug, is_active=True)
		return qs

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context['category'] = self.category

		return context


class ArticleDetailView(ArticleDetailAccessMixin, DetailView):
	model = Article
	template_name = "article/article_detail.html"
	slug_field = 'slug'
	slug_url_kwarg = 'article'

	def setup(self, request, *args, **kwargs):
		self.category = Category.objects.get(slug=kwargs['category'])
		return super().setup(request, *args, **kwargs)

	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)

		current_article_id = self.get_object().id
		slug = self.kwargs['category']

		context['article_list'] = Article.objects.filter(
			category__slug=slug, is_active=True
		).exclude(
			id=current_article_id
		).order_by('-date_pub')[:3]
		
		return context


class SearchResultsView(ListView):
	model = Article
	template_name = "article/search_results.html"

	def get_queryset(self):
		if self.request.method == 'GET':
			query = self.request.GET.get('search_input')
			result = Article.objects.filter(Q(title__icontains=query))
			return result

		return Article.Objects.all().order_by('-date_pub')