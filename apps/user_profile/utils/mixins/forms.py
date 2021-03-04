from crispy_forms.helper import FormHelper
from django import forms


class CrispyMixin:
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.helper = FormHelper()
		self.helper.form_show_labels = False


class CrispyRequestMixin(CrispyMixin):
	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request
		self.user = request.user
		self.profile = self.user.userprofile