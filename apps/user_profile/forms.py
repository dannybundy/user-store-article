import re

from crispy_forms.helper import FormHelper

from django import forms
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import (
	AuthenticationForm,
	PasswordResetForm,
	SetPasswordForm,
	UserCreationForm
)
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from phonenumber_field.phonenumber import PhoneNumber
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

from .models import UserProfile

from .utils.mixins.forms import *
from .utils.helper_functions.forms import *
from .utils.helper_functions.twilio import *



FIRST_MAX = 30
LAST_MAX = 30
EMAIL_MAX = 30
USER_MAX = 30
PASS_MAX = 30

AC_MAX = 5
NUM_MAX = 15

CODE_MAX = 10

TOKEN_LENGTH = 20


# Used as an inherited class for the other forms
class PasswordForm(CrispyMixin, forms.Form):
	first_name = forms.CharField(
		max_length=FIRST_MAX,
		widget=forms.TextInput(attrs={'maxlength':FIRST_MAX, 'placeholder': "Al"})
	)
	last_name = forms.CharField(
		max_length=LAST_MAX,
		widget=forms.TextInput(attrs={'maxlength':LAST_MAX, 'placeholder': "Bundy"})
	)
	email = forms.CharField(
		max_length=EMAIL_MAX,
		widget=forms.TextInput(attrs={'maxlength':EMAIL_MAX, 'placeholder': "biguns84@gmail.com"})
	)
	username = forms.CharField(
		max_length=USER_MAX,
		widget=forms.TextInput(attrs={'maxlength':USER_MAX, 'placeholder': "Al"})
	)
	password = forms.CharField(
		max_length=PASS_MAX,
		strip=False,
		widget=forms.PasswordInput({'maxlength':PASS_MAX})
	)

	def clean(self):
		error_list = []
		password = self.cleaned_data.get('password')

		if password is not None:
			if len(password) < 8:
				error_list.append("Password is not at least 8 characters.")
			if not re.search("[a-zA-Z]", password):
				error_list.append("Password does not contain a letter.")
			if not re.search("[0-9]", password):
				error_list.append("Password does not contain a number.")
			if not re.search(r"[!#$%&'()*+,-./:;<=>?@[\]^_`{|}~]", password):
				error_list.append("Password does not contain a special character.")

			first_name = self.cleaned_data.get('first_name')
			if first_name is not None:
				if len(first_name) > 4 and first_name.lower() in password.lower():
					error_list.append("Password contains your first name.")

			last_name = self.cleaned_data.get('last_name')
			if last_name is not None:
				if len(last_name) > 4 and last_name.lower() in password.lower():
					error_list.append("Password contains your last name.")

			email = self.cleaned_data.get('email')
			if email is not None:
				email_name=email.split("@")[0]
				if len(email_name) > 4 and email_name.lower() in password.lower():
					error_list.append("Password contains your email.")

			username = self.cleaned_data.get('username')
			if username is not None:
				if len(username) > 4 and username.lower() in password.lower():
					error_list.append("Password contains your username.")

			if len(error_list) > 0:
				raise forms.ValidationError({'password': error_list})

		return self.cleaned_data


class CustomRegistrationForm(PasswordForm, forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'username', 'password')

	def clean_email(self):
		email = self.cleaned_data.get('email')
		if User.objects.filter(email=email).exists():
			raise forms.ValidationError("Email already exists in the system.")	
		return email

	def clean_username(self):
		username = self.cleaned_data.get('username')
		if User.objects.filter(username__iexact=username).exists():
			raise forms.ValidationError("Username already exists in the system.")
		
		elif 'guest' in username.lower():
			raise forms.ValidationError("Cannot create a user with this username.")

		return username

	def save(self, commit=True):
		user = super().save(commit=False)
		user.set_password(self.cleaned_data.get("password"))
		
		if commit:
			user.save()

		return user


class CustomAuthenticationForm(AuthenticationForm):
	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request
		self.user_cache = None

		self.fields['username'].max_length = USER_MAX
		self.fields['username'].widget.attrs = {
			'aria-describedby': 'username-addon',
			'class': 'form-control',
			'maxlength': USER_MAX,
			'label': ''
		}

		self.fields['password'].max_length = PASS_MAX
		self.fields['password'].widget.attrs = {
			'aria-describedby': 'password-addon',
			'class': 'form-control',
			'maxlength': PASS_MAX,
			'label': ''
		}

	def clean(self):
		username = self.cleaned_data.get('username')
		password = self.cleaned_data.get('password')

		profile_qs = UserProfile.objects.filter(
			user__username=username,
			user__is_active=True
		)

		if profile_qs.exists():
			profile = profile_qs[0]

			if profile.perm_lockout():
				raise forms.ValidationError(
					{
					'username': 
					"You have attempted to log in too many times. Please reset password."
					}
				)

			if profile.temp_lockout():
				if profile.lockout_over():
					profile.add_lockout()
				else:
					raise forms.ValidationError(
						{
						'username': 
						"You have attempted to log in too many times. Please try again later."
						}
					)
			
		if username is not None and password is not None:
			self.user_cache = authenticate(
				self.request,
				username=username,
				password=password
			)
			
			if not self.user_cache:
				if profile_qs.exists():
					profile.add_attempt()
				
				raise forms.ValidationError(
					{
					'username': 
					"Username or password is incorrect. Please try again."
					}
				)
			else:
				user = User.objects.get(username=username)
				if user.last_login is None:
					self.request.session['first_login'] = "first time logging in"

				profile.reset_values()
				self.confirm_login_allowed(self.user_cache)

		return self.cleaned_data


class CustomPasswordChangeForm(CrispyRequestMixin, PasswordForm):
	old_password = forms.CharField(
		max_length=PASS_MAX,
		strip=False,
		widget=forms.PasswordInput({'maxlength': PASS_MAX})
	)

	def clean_old_password(self):
		old_password = self.cleaned_data.get('old_password')
		password = self.cleaned_data.get('password')

		if not self.user.check_password(old_password):
			self.request.session['old_password_incorrect'] = True
			raise forms.ValidationError(
				"Old password is incorrect. Please try again."
			)

		self.request.session.pop('old_password_incorrect', None)
		if password and old_password:
			if password.lower() == old_password.lower():
				raise forms.ValidationError(
					"Cannot set new password as old password. Please try again."
				)

		return old_password

	def save(self, commit=True):
		password = self.cleaned_data.get('password')
		self.user.set_password(password)

		if commit:
			self.user.save()
			self.profile.reset_values()
			logout(self.request)


class PhonenumberForm(forms.Form):
	country_code = CountryField().formfield(
		initial='US',
		required=False,
		widget=CountrySelectWidget(
			attrs={
				'aria-describedby': 'number-addon',
				'class': 'form-control',
				'style': 'width: 0px; display: inline-block'
			}
		)
	)
	area_code = forms.CharField(
		max_length=AC_MAX,
		required=False,
		widget=forms.TextInput(
			attrs={
				'class': 'form-control',
				'placeholder': '626',
				'maxlength': AC_MAX,
				'style': 'width: 60px; display: inline-block'
			}
		)
	)
	number = forms.CharField(
		max_length=NUM_MAX,
		required=False,
		widget=forms.TextInput(
			attrs={
				'class': 'form-control',
				'placeholder': '3982102',
				'maxlength': NUM_MAX,
				'style': 'width: 100px; display: inline-block'
			}
		)
	)

	phonenumber = forms.CharField(max_length=0, required=False)

	def clean_phonenumber(self):
		clean = self.cleaned_data

		country_code = clean.get('country_code')
		area_code = clean.get('area_code')
		number = clean.get('number')
		phonenumber = None

		if area_code or number:
			if not (area_code and number):
				raise forms.ValidationError("Please fill in blank fields.")

			if re.search('[a-zA-Z]', area_code) or re.search('[a-zA-Z]', number):
				raise forms.ValidationError(
					"Use only numbers. Please try again."
				)

			phonenumber = PhoneNumber.from_string(
				phone_number=f"{area_code}{number}", region=country_code
			).as_e164

		return phonenumber


class ResetForm(PasswordResetForm, PhonenumberForm):
	def __init__(self, request, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request

		self.fields['email'].max_length = EMAIL_MAX
		self.fields['email'].required = False
		self.fields['email'].widget.attrs = {
			'aria-describedby': 'email-addon',
			'class': 'form-control',
			'maxlength': EMAIL_MAX,
		}

	def clean(self):
		phonenumber = self.cleaned_data.get('phonenumber')
		email = self.cleaned_data.get('email')

		if not (phonenumber or email):
			raise forms.ValidationError("Please enter a valid email or phone number.")

		elif phonenumber and email:
			raise forms.ValidationError("Please choose either an email or phone number.")

		return self.cleaned_data

	def send_text(self, reset_password=True):
		phonenumber = self.cleaned_data.get('phonenumber')
		profile_qs = UserProfile.objects.filter(phonenumber=phonenumber)
		
		subject_name = "Username"
		if reset_password:
			subject_name = "Reset Password Link"

		if profile_qs.exists():
			profile = profile_qs[0]

			if profile.allow_send_msg():
				if profile.verified_number:
					profile_qs.update(send_msg_time = timezone.now())

					if reset_password:
						token = default_token_generator.make_token(profile.user)
						uid = urlsafe_base64_encode(force_bytes(profile.user.pk))
						url_part = reverse_lazy(
							'profile:password_reset_confirm', kwargs={'uidb64': uid, 'token': token}
						)
						url = self.request.build_absolute_uri(url_part)
						body = f"Change your password with this link: {url}"
						twilio_auth(profile, body)

						# Saves values into session to retrieve account success in
						# "CustomPasswordResetConfirmView" and to prevent malicious
						# users from accessing that page
						self.request.session['phonenumber'] = phonenumber
						self.request.session['extra_reset_token'] = random_string(TOKEN_LENGTH)
					else:
						body = f"This is your username: {profile.user.username}"
						twilio_auth(profile, body)

					messages.success(self.request, f"{subject_name} has been sent to your phone.")

				else:
					messages.warning(
						self.request,
						"""You have not verified your phone number yet. Please try using
						your email
						"""
					)
					return reverse('profile:password_reset_request')
			else:
				messages.warning(
					self.request,
					f"""Please wait {profile.send_msg_wait_time()} seconds
					before requesting another reset.
					"""
				)
		else:
			# User entered a wrong phone number but it will still say that the link was sent
			# to prevents malicious users from guessing if someone's phone number exists within 
			# the system
			messages.success(self.request, f"{subject_name} has been sent to your phone.")

		return reverse('profile:login')

	def pre_send_email(self, reset_password=True):
		email = self.cleaned_data.get('email')
		profile_qs = UserProfile.objects.filter(email=email)

		subject_name = "Username"
		if reset_password:
			subject_name = "Reset Password Link"

		if profile_qs.exists():
			profile = profile_qs[0]

			if profile.allow_send_msg():
				profile_qs.update(send_msg_time=timezone.now())

				self.request.session['email'] = email
				if reset_password:
					self.request.session['extra_reset_token'] = random_string(TOKEN_LENGTH)
				
				# Email is sent in inherited 'PasswordResetForm' function 'send_mail()'
				messages.success(
					self.request,
					f"""{subject_name} has been sent to your email. If it is is not in
					your inbox, check your spam mail.
					"""
				)
				return None
			else:
				messages.warning(
					self.request,
					f"""Please wait {profile.send_msg_wait_time()} seconds before
					requesting another reset link.
					"""
				)
		else:
			messages.success(
				self.request,
				f"""{subject_name} has been sent to your email. If the link is not in your
				inbox, check your spam mail.
				"""
			)

		return reverse('profile:login')


class CustomSetPasswordForm(PasswordForm):
	def __init__(self, request, user, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.request = request
		self.user = user


	def clean_password(self):
		password = self.cleaned_data.get('password')
		if self.user.check_password(password):
			raise forms.ValidationError(
				"Cannot set new password as old password. Please try again."
			)
		return password

	def save(self, commit=True):
		password = self.cleaned_data.get('password')
		self.user.set_password(password)

		if commit:
			self.user.userprofile.reset_values()
			self.user.save()
	
			self.request.session.pop('extra_reset_token', None)
			self.request.session.pop('email', None)
			self.request.session.pop('phonenumber', None)


class PasswordValidationForm(CrispyRequestMixin, forms.Form):
	password = forms.CharField(
		max_length=PASS_MAX,
		strip=False,
		widget=forms.PasswordInput({'maxlength': PASS_MAX})
	)

	def clean_password(self):
		password = self.cleaned_data.get('password')

		if self.user.check_password(password):
			self.profile.reset_values()
		else:
			self.profile.add_attempt()
			raise forms.ValidationError("Invalid password. Please try again.")

		return password


class AddPhonenumberForm(CrispyRequestMixin, PhonenumberForm):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['country_code'].required = True
		self.fields['area_code'].required = True
		self.fields['number'].required = True
	
	def clean(self):
		phonenumber = self.cleaned_data.get('phonenumber')
		url = reverse('profile:profile')

		if phonenumber is not None:
			profile_qs = UserProfile.objects.filter(phonenumber=phonenumber, verified_number=True)
			profile_phonenumber = phonenumber != self.profile.phonenumber

			if profile_qs.exists() and not profile_phonenumber:
				raise forms.ValidationError(
					{'phonenumber': "Validated phone number already exists within the system."}
				)
			else:
				url = reverse('profile:phone_verification')
				code_sent = twilio_send_code(self.profile, phonenumber)
				if not code_sent:
					raise forms.ValidationError(
						{'phonenumber': "Phone number was not valid. Please try again."}
					)
		
				messages.success(
					self.request,
					"""<b>Phone number</b> has been updated. Check your phone for
					the verification code.
					"""
				)

		self.request.session['url'] = url
		return self.cleaned_data


class UpdateProfileForm(AddPhonenumberForm, forms.ModelForm):
	class Meta:
		model = User
		fields = (
			'first_name',
			'last_name',
			'email',

			'country_code',
			'area_code',
			'number',
			'phonenumber',
		)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields['first_name'].max_length = FIRST_MAX
		self.fields['first_name'].required = True
		self.fields['first_name'].widget.attrs = {'maxlength': FIRST_MAX}

		self.fields['last_name'].max_length = LAST_MAX
		self.fields['last_name'].required = True
		self.fields['last_name'].widget.attrs = {'maxlength': LAST_MAX}

		self.fields['email'].max_length = EMAIL_MAX
		self.fields['email'].required = True
		self.fields['email'].widget.attrs = {'maxlength': EMAIL_MAX}

		self.fields['country_code'].required = False
		self.fields['area_code'].required = False
		self.fields['number'].required = False

	def clean_first_name(self):
		first_name = self.cleaned_data.get('first_name')

		if self.user.first_name != first_name:
			self.user.first_name = first_name
			self.user.save()
			messages.success(self.request, "<b>First Name</b> updated.")

		return first_name

	def clean_last_name(self):
		last_name = self.cleaned_data.get('last_name')

		if self.user.last_name != last_name:
			self.user.last_name = last_name
			self.user.save()
			messages.success(self.request, "<b>Last Name</b> updated.")	

		return last_name

	def clean_email(self):
		email = self.cleaned_data.get('email')

		if email != self.profile.email and UserProfile.objects.filter(email=email).exists():
			raise forms.ValidationError("Email already exists in the system.")
		
		if self.user.email != email:
			self.user.email = email
			self.user.save()
			messages.success(self.request, "<b>Email</b> updated.")	

		return email


class CodeVerificationForm(CrispyRequestMixin, forms.Form):
	code = forms.CharField(
		max_length=CODE_MAX,
		required=False,
		widget=forms.TextInput(
			attrs={'maxlength': CODE_MAX,'placeholder': 'Enter code'}
		)
	)

	def clean_code(self):
		code = self.cleaned_data.get('code')

		if not code or code is None:
			raise forms.ValidationError("Please enter a code.")

		approved = twilio_verify_code(self.profile, code)
		if not approved:
			raise forms.ValidationError(
				"Verification code is incorrect. Please try again."
			)