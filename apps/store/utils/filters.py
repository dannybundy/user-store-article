from store.models import *



def get_all_possible_filters(item_category):
	"""Returns a list of 'FilterOption' PKs for each 'FilterCategory' set within the
	current 'ItemCategory'
	"""

	pk_lists = []

	for filter_category in FilterCategory.objects.filter(item_category=item_category):
		filter_option_set = filter_category.filteroption_set.all()
		temp_list = list(filter_option_set.values_list('pk', flat=True))

		pk_lists.append(temp_list)

	return pk_lists


def filter_item_list(item_category, item_list, chosen_filters):	
	"""First for loop: 'and' filter.
	   Second for loop: 'or' filter.
	"""
	
	for filter_option_set in get_all_possible_filters(item_category):
		temp_list = []

		for pk in chosen_filters:
			if pk in filter_option_set:
				temp_list.append(pk)

		if len(temp_list) > 0:
			item_list = item_list.filter(filter_option__pk__in=temp_list).distinct()

	return item_list