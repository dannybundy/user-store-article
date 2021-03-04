import datetime, json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import (
	LogoutView,
	PasswordChangeView,
	PasswordResetView,
	PasswordResetConfirmView
)
from django.contrib.messages.views import SuccessMessageMixin
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import (
	DetailView,
	FormView,
	TemplateView,
	UpdateView,
	View
)

from phonenumber_field.phonenumber import PhoneNumber

from .forms import *
from .models import *
from .utils.helper_functions.views import *
from .utils.helper_functions.twilio import twilio_send_code
from .utils.mixins.access import *
from .utils.mixins.views import *



class CustomRegistrationView(AnonymousAccessMixin,
							SuccessMessageMixin,
							AjaxValidateFormMixin,
							FormView):
	form_class = CustomRegistrationForm
	template_name = 'auth/register.html'
	success_url = reverse_lazy('profile:login')
	success_message = "Successfully created account!"

	def post(self, *args, **kwargs):
		if self.request.is_ajax():
			deserialize_json(self.request)

		return super().post(self.request, **kwargs)


class CustomAuthenticationView(AnonymousAccessMixin,
								RequestFormMixin,
								AjaxValidateFormMixin,
								FormView):
	form_class = CustomAuthenticationForm
	template_name = 'auth/login.html'
	success_url = reverse_lazy('profile:home')

	def form_valid(self, form):
		username = self.request.POST['username']
		password = self.request.POST['password']

		user = authenticate(username=username, password=password)
		first_login = self.request.session.get('first_login')

		login(self.request, user)
		if first_login is not None:
			if self.request.is_ajax():
				url = reverse_lazy('profile:add_phone')
				data = {'url': url}
				return JsonResponse(data, status=200)

			return redirect('profile:add_phone')


		if self.request.is_ajax():
			url = reverse_lazy('profile:home')
			data = {'url': url}
			return JsonResponse(data, status=200)
		
		return redirect(self.success_url)


class LogoutView(LogoutView):
	next_page = 'profile:home'


class CustomPasswordChangeView(ChangeAccessMixin,
								SuccessMessageMixin,
								ChangePasswordFormMixin,
								FormView):
	form_class = CustomPasswordChangeForm
	template_name = 'auth/password_change_form.html'
	success_url = reverse_lazy('profile:login')
	success_message = "Your password has been changed."

	def form_invalid(self, form):
		if self.request.is_ajax():
			return super().form_invalid(form)
		
		incorrect = self.request.session.get('old_password_incorrect')
		if incorrect is not None:
			self.profile.add_attempt()
			url = check_for_lockout(self.request, self.profile)
			if url is not None:
				return redirect(url)

		return super().form_invalid(form)


class CustomPasswordResetView(AnonymousAccessMixin,
								RequestFormMixin,
								PasswordResetView):
	form_class = ResetForm
	success_url = reverse_lazy('profile:login')
	template_name = 'auth/password_reset_form.html'

	email_template_name = 'auth/password_reset_email.html'
	subject_template_name = 'auth/password_reset_subject.txt'
	html_email_template_name = "auth/password_reset_html_email.html"
	extra_email_context = None
	from_email = None
	title = ('Forgot Password')
	token_generator = default_token_generator

	def form_valid(self, form):
		phonenumber = form.cleaned_data.get('phonenumber')
		if phonenumber is not None:
			url = form.send_text()
			return redirect(url)


		url = form.pre_send_email()
		if url is not None:  #email doesn't exist in the system.
			return redirect(url)

		opts = {
			'request': self.request,
			'use_https': self.request.is_secure(),
			'token_generator': self.token_generator,
			'email_template_name': self.email_template_name,
			'html_email_template_name': self.html_email_template_name,
			'subject_template_name': self.subject_template_name,
			'extra_email_context': self.extra_email_context,
			'from_email': self.from_email,
		}

		# Sends email in inherited 'PasswordResetForm' method 'send_mail()'
		form.save(**opts)
		return redirect(self.success_url)


class CustomPasswordResetConfirmView(ResetAccessMixin,
									SuccessMessageMixin,
									ChangePasswordFormMixin,
									PasswordResetConfirmView):
	form_class = CustomSetPasswordForm
	success_url = reverse_lazy('profile:login')
	template_name = 'auth/password_reset_confirm.html'
	success_message = "Password has been successfully reset!"

	post_reset_login = False
	post_reset_login_backend = None
	reset_url_token = "set-password"
	title = "Enter new password"
	token_generator = default_token_generator

	profile = None

	def setup(self, request, *args, **kwargs):
		self.profile = get_profile(request)
		return super().setup(request, *args, **kwargs)


class RecoverUsernameView(AnonymousAccessMixin,
							RequestFormMixin,
							PasswordResetView):
	form_class = ResetForm
	template_name = 'auth/recover_username.html'
	success_url = reverse_lazy('profile:login')

	email_template_name = 'auth/recover_username_email.html'
	subject_template_name = 'auth/recover_username_subject.txt'
	html_email_template_name = 'auth/recover_username_html_email.html'
	extra_email_context = None
	from_email = None
	title = ('Forgot Username')
	token_generator = default_token_generator


	def form_valid(self, form):
		phonenumber = form.cleaned_data.get('phonenumber')
		if phonenumber is not None:
			url = form.send_text(reset_password=False)
			return redirect(url)


		url = form.pre_send_email(reset_password=False)
		if url is not None: 
			return redirect(url)

		email = self.request.POST['email']
		profile = UserProfile.objects.get(email=email)

		opts = {
			'request': self.request,
			'use_https': self.request.is_secure(),
			'token_generator': self.token_generator,
			'email_template_name': self.email_template_name,
			'html_email_template_name': self.html_email_template_name,
			'subject_template_name': self.subject_template_name,
			'extra_email_context': {'username': profile.user},
			'from_email': self.from_email,
		}

		form.save(**opts)
		return redirect(self.success_url)


# If JS is disabled
class PasswordValidationView(ValidationAccessMixin, RequestFormMixin, FormView):
	form_class = PasswordValidationForm
	template_name = 'user_profile/verify_password.html'
	success_url = reverse_lazy('profile:profile')
	
	def form_invalid(self, form):
		url = check_for_lockout(self.request, self.profile)
		if url is not None:
			return redirect(url)

		return super().form_invalid(form)


# If JS is enabled
def ajax_password_validation_view(request):
	if request.is_ajax():
		profile = request.user.userprofile

		form = PasswordValidationForm(request, request.POST)
		if form.is_valid():
			data = {'refresh': "Correct info."}
		else:
			data = {'error_list': form.errors}
			if profile.temp_lockout():
				data = {'refresh': "Too many attempts."}

		return JsonResponse(data, status=200)



class HomeView(TemplateView):
	template_name = 'user_profile/home.html'


class AddPhoneView(AddPhoneAccessMixin, RequestFormMixin, FormView):
	form_class = AddPhonenumberForm
	template_name = 'user_profile/add_phone.html'
	success_url = reverse_lazy('profile:phone_verification')

	def post(self, *args, **kwargs):	
		later = self.request.POST.get('later')
		if later is not None:
			self.request.session.pop('first_login', None)
			return redirect('profile:home')

		return super().post(self.request, **kwargs)

	def form_valid(self, form):
		self.request.session.pop('first_login', None)
		return super().form_valid(form)


class PhoneVerificationView(VerifyCodeAccessMixin,
							SuccessMessageMixin,
							RequestFormMixin,
							FormView):
	form_class = CodeVerificationForm
	template_name = 'user_profile/phone_verification.html'
	success_url = reverse_lazy('profile:profile')
	success_message = "Phone number has been verified!"

	def post(self, *args, **kwargs):
		send_again = self.request.POST.get('resend_code')

		if send_again is not None:
			twilio_send_code(self.profile, self.profile.phonenumber)
			messages.info(self.request, "Code has been resent to your phone.")
			return redirect(self.request.path_info)

		return super().post(*args, **kwargs)


class ProfileView(LoginAccessMixin, VerifyPasswordContextMixin, DetailView):
	model = UserProfile
	template_name = 'user_profile/profile.html'

	def get_object(self, queryset=None):
		return self.request.user


class UpdateProfileView(LoginAccessMixin,
						RequestFormMixin,
						VerifyPasswordContextMixin,
						UpdateView):
	form_class = UpdateProfileForm
	model = User
	template_name = 'user_profile/update_profile.html'

	def get_object(self, queryset=None):
		return self.request.user

	def post(self, *args, **kwargs):
		disable = self.request.POST.get('disable')
		if disable is not None:
			self.profile.disable_account()
			messages.warning(
				self.request, "Sorry to see you go. Contact us if you wanna come back!"
			)
			return redirect('profile:login')

		return super().post(*args, **kwargs)

	def get_success_url(self, **kwargs):
		url = self.request.session['url']
		del self.request.session['url']

		return url