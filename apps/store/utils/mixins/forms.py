from user_profile.utils.mixins.forms import CrispyMixin

class CrispyCustomerMixin(CrispyMixin):
	def __init__(self, customer, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.customer = customer