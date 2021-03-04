from django.test import TestCase
from model_bakery import baker

from store.utils.filters import *
from store.models import *
from .utils.helper_functions import *


class TestFilterFunctions(BaseItemTest):
	def test_get_all_possible_filters(self):
		val = self.items_with_filter_options()
		item_category = val[0]
		filter_option = val[1]

		pk_lists = get_all_possible_filters(item_category)

		self.assertEqual(len(pk_lists), 5)
		self.assertIn([filter_option.pk], pk_lists)

	def test_filter_item_list(self):
		val = self.items_with_filter_options()
		item_category = val[0]
		filter_option = val[1]

		item_list = Item.objects.all()
		chosen_filters = [filter_option.pk]

		item_list = filter_item_list(item_category, item_list, chosen_filters)
		test_item = Item.objects.filter(filter_option__pk=filter_option.pk)[0]

		self.assertEqual(len(item_list), 1)
		self.assertIn(test_item, item_list)