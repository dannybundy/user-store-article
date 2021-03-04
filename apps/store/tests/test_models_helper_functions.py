from django.core import mail
from store.utils.helper_functions.models import *

from .utils.helper_functions import *


class TestModelHelperFunctions(TestCase):
	def test_create_ref_code_length(self):
		ref_code = create_ref_code()
		self.assertEqual(len(ref_code), 20)