from django.urls import path
from store import views

app_name='store'

urlpatterns = [	
	path('billing_profile/', views.BillingProfileView.as_view(), name='billing_profile'),
	path('cards/', views.CardView.as_view(), name='card'),
	path('shipping_address/', views.ShippingAddressView.as_view(), name='shipping_address'),
	path('order_history/', views.OrderHistoryView.as_view(), name='order_history'),

	path('order_summary/', views.OrderSummaryView.as_view(), name='order_summary'),
	path('checkout/', views.CheckoutView.as_view(), name='checkout'),

	path('', views.ItemCategoryListView.as_view(), name='item_category_list'),
	path('search_results/', views.SearchResultsView.as_view(), name='search_results'),

	path('<slug:item_category>/', views.ItemListView.as_view(), name='item_list'),
	path('<slug:item_category>/<slug:item>/', views.ItemDetailView.as_view(), name='item_detail'),
]