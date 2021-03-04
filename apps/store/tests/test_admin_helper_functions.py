from django.test import TestCase
from model_bakery import baker

from store.admin.utils.helper_functions import *
from store.models import Order


class TestAdminHelperFunctions(TestCase):
	def test_hide_admin_btns(self):
		extra_context = {
			'show_save_and_continue': True,
			'show_save_and_add_another': True,
			'close': True
		}
		
		extra_context = hide_admin_btns(extra_context)

		test_extra_context = {
			'show_save_and_continue': False,
			'show_save_and_add_another': False,
			'close': False
		}

		self.assertEqual(extra_context, test_extra_context)

	def test_get_user_or_guest(self):
		obj = baker.make(Order)
		self.assertEqual(get_user_or_guest(obj), f"Guest {obj.customer.guest_num}")