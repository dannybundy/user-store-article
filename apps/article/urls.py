from django.urls import path
from article import views

app_name = "article"

urlpatterns = [
	path('', views.CategoryListView.as_view(), name="category_list"),
	path('search_results/', views.SearchResultsView.as_view(), name="search_results"),

	path('<slug:category>/', views.ArticleListView.as_view(), name="article_list"),
	path('<slug:category>/<slug:article>', views.ArticleDetailView.as_view(), name="article_detail"),
]