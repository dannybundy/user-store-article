from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse


class CustomTestMixin(UserPassesTestMixin):
	msg = None
	url = None

	def get_base_test(self):
		return True

	def dispatch(self, request, *args, **kwargs):
		base_test_result = self.get_base_test()

		if not base_test_result:
			return self.handle_no_permission()
	
		return super().dispatch(request, *args, **kwargs)

	def test_func(self):
		return True

	def handle_no_permission(self):
		if self.msg is not None:
			messages.warning(self.request, self.msg)
	
		return redirect(self.url)



class AnonymousAccessMixin(CustomTestMixin):
	def get_base_test(self):
		self.url = reverse('profile:home')
		return self.request.user.is_anonymous


class ResetAccessMixin(AnonymousAccessMixin):
	def test_func(self):
		if self.profile is None:
			return False

		if self.profile.is_showcase_user():
			self.msg = "This account's password cannot be changed."
			return False

		token = self.request.session.get('extra_reset_token')
		if token is None:
			self.msg = f"""Please use the same device and browser you used to request this link.
				If the link is still redirecting you to another page, request another link.
				"""
			return False

		return True




class LoginAccessMixin(CustomTestMixin):
	profile = None

	def get_base_test(self):
		self.url = reverse('profile:login')

		user = self.request.user
		if not user.is_authenticated:
			return False

		self.profile = user.userprofile		
		if self.profile.temp_lockout():
			logout(self.request)
			self.msg = "You have attempted to log in too many times. Please try again later."
			return False

		return True


class ChangeAccessMixin(LoginAccessMixin):
	def test_func(self):
		if self.profile.is_showcase_user():
			self.url = reverse('profile:home')
			self.msg = "This account's password cannot be changed."
			return False

		return True


class AddPhoneAccessMixin(LoginAccessMixin):
	def test_func(self):
		self.url = reverse('profile:update_profile')
		first_login = self.request.session.get('first_login')
		return not first_login is None


class VerifyCodeAccessMixin(LoginAccessMixin):
	def test_func(self):
		if self.profile.phonenumber and not self.profile.verified_number:
			return True

		self.url = reverse('profile:home')
		self.msg = "You have no new number to verify."
		return False


class ValidationAccessMixin(LoginAccessMixin):	
	def test_func(self):
		self.url = reverse('profile:profile')
		return self.profile.validation_required()