from django.core import mail
from django.test import TestCase
from store.utils.helper_functions.forms import *

from .utils.helper_functions import *


class TestFormHelperFunctions(BaseItemTest):
	def test_send_order_email_outbox_length(self):
		order_item = self.order_item_ordered()
		order = order_item.order
		send_order_email(order)
		test_subject_str = "Website Store: Someone bought some things"

		self.assertEqual(len(mail.outbox), 2)
		self.assertEqual(mail.outbox[1].subject, test_subject_str)