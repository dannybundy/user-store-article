import re

from dateutil.relativedelta import *
from django.conf import settings
from django.core import mail
from django.test import TestCase
from model_bakery import baker

from user_profile.forms import *
from user_profile.models import *
from .helper.constants import *
from .helper.functions import *


class PasswordFormTest(BaseUserTest):
	def test_valid_form(self):
		data = self.valid_user_data()
		form = PasswordForm(data)
		self.assertTrue(form.is_valid())

	def test_invalid_form_password_error_length_letter_special_char(self):
		data = self.valid_user_data()
		data['password'] = '1'
		form = PasswordForm(data)

		self.assertFalse(form.is_valid())
		error_list = form.errors['password']
		
		self.assertIn(PASS_LENGTH_ERROR, error_list)
		self.assertIn(PASS_LETTER_ERROR, error_list)
		self.assertIn(PASS_SPECIAL_CHAR_ERROR, error_list)

	def test_invalid_form_password_error_contains_first_last_email_user(self):
		data = self.valid_user_data()
		data['password'] = f"{VALID_FIRST}{VALID_LAST}{VALID_EMAIL}{VALID_USER}"
		form = PasswordForm(data)

		self.assertFalse(form.is_valid())
		error_list = form.errors['password']

		self.assertIn(PASS_FIRST_ERROR, error_list)
		self.assertIn(PASS_LAST_ERROR, error_list)
		self.assertIn(PASS_EMAIL_ERROR, error_list)
		self.assertIn(PASS_USER_ERROR, error_list)


class CustomRegistrationFormTest(BaseUserTest):
	def test_valid_data(self):
		data = self.valid_user_data()
		form = CustomRegistrationForm(data)
		
		self.assertTrue(form.is_valid())
		form.save()
	
		total_user_count = User.objects.all().count()
		self.assertEquals(total_user_count, 1)

	def test_invalid_data_email_already_exists(self):
		baker.make(User, email=VALID_EMAIL)
		data = self.valid_user_data()
		form = CustomRegistrationForm(data)

		self.assertFalse(form.is_valid())
		self.assertTrue(EMAIL_ERROR in form.errors['email'])
	
	def test_invalid_data_username_already_exists(self):
		baker.make(User, username=VALID_USER)
		data = self.valid_user_data()
		form = CustomRegistrationForm(data)

		self.assertFalse(form.is_valid())
		self.assertTrue(USER_ERROR in form.errors['username'])


class CustomAuthenticationFormTest(BaseUserTest):
	def test_authentication_approved(self):
		user = self.new_user()
		data = {'username': user.username, 'password': VALID_PASS_1}
		url = reverse('profile:login')
		response = self.client.get(url)

		form = CustomAuthenticationForm(response.wsgi_request, data=data)

		self.assertTrue(form.is_valid())

	def test_lockout_error(self):
		user = self.new_user()
		UserProfile.objects.filter(user=user).update(login_attempt=5)

		data = {'username': user.username, 'password': VALID_PASS_1}
		url = reverse('profile:login')
		response = self.client.get(url)

		form = CustomAuthenticationForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(TEMP_LOCKOUT_ERROR, form.errors['username'])


class CustomPasswordChangeFormTest(BaseUserTest):
	def test_valid_form(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		old_password = data['password']

		data['old_password'] = old_password
		data['password'] = VALID_PASS_2

		url = reverse('profile:password_change')
		response = self.client.get(url)
		form = CustomPasswordChangeForm(response.wsgi_request, data=data)

		self.assertTrue(form.is_valid())

	def test_invalid_form_old_password_is_incorrect(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		data['old_password'] = VALID_PASS_2
		data['password'] = VALID_PASS_1

		url = reverse('profile:password_change')
		response = self.client.get(url)
		form = CustomPasswordChangeForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(OLD_PASS_INCORRECT_ERROR, form.errors['old_password'])

	def test_invalid_form_new_password_is_same_as_old_password(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		old_password = data['password']

		data['old_password'] = old_password
		data['password'] = old_password

		url = reverse('profile:password_change')
		response = self.client.get(url)
		form = CustomPasswordChangeForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(NEW_SAME_AS_OLD_ERROR, form.errors['old_password'])


class PhonenumberFormTest(BaseUserTest):
	def test_valid_form(self):
		data = self.valid_phone_data()
		form = PhonenumberForm(data)
		self.assertTrue(form.is_valid())

	def test_invalid_form_letter_in_area_code_and_number(self):
		data = self.valid_phone_data()
		data['area_code'] = 'van'
		data['number'] = 'halen'
		form = PhonenumberForm(data)
		
		self.assertFalse(form.is_valid())
		self.assertIn(PHONE_LETTER_ERROR, form.errors['phonenumber'])

	def test_invalid_form_empty_field(self):
		data = self.valid_phone_data()
		data['area_code'] = 'van'
		data['number'] = ''
		form = PhonenumberForm(data)
		
		self.assertFalse(form.is_valid())
		self.assertIn(EMPTY_PHONE_ERROR, form.errors['phonenumber'])


class ResetFormTest(BaseUserTest):
	def test_valid_form_pre_send_email(self):
		user = self.new_user()
		self.client.force_login(user)
		data = {'email': user.email}

		url = reverse('profile:password_reset_request')
		response = self.client.get(url)
		form = ResetForm(response.wsgi_request, data=data)

		self.assertTrue(form.is_valid())
		self.assertIs(form.pre_send_email(), None)

	def test_valid_form_send_text(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_phone_data()
		self.attach_phonenumber(user, data)

		url = reverse('profile:password_reset_request')
		response = self.client.get(url)
		request = response.wsgi_request
		form = ResetForm(request, data=data)

		self.assertTrue(form.is_valid())

		form.send_text()
		self.assertEquals(request.session.get('phonenumber'), user.userprofile.phonenumber)

	def test_invalid_form_email_and_phonenumber(self):
		user = self.new_user()
		self.client.force_login(user)
		data = self.valid_phone_data()
		data['email'] = user.email

		url = reverse('profile:password_reset_request')
		response = self.client.get(url)
		form = ResetForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(EMAIL_AND_PHONE_ERROR, form.errors['__all__'])


class AddPhonenumberFormTest(BaseUserTest):
	def test_valid_form(self):
		user = self.new_user()
		self.client.force_login(user)

		session = self.client.session
		session['first_login'] = "first time logging in"
		session.save()

		url = reverse('profile:add_phone')
		data = self.valid_phone_data()
		response = self.client.get(url, data)
		request = response.wsgi_request
		form = AddPhonenumberForm(request, data=data)

		self.assertTrue(form.is_valid())
		self.assertIsNot(request.user.userprofile.phonenumber, None)

	def test_invalid_form_phonenumber_already_exists(self):
		user = self.new_user()
		data = self.valid_phone_data()
		self.attach_phonenumber(user, data)
		self.client.force_login(user)

		url = reverse('profile:add_phone')
		response = self.client.get(url)
		form = AddPhonenumberForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(PHONE_EXISTS_ERROR, form.errors['phonenumber'])

	def test_invalid_form_phonenumber_already_exists(self):
		user = self.new_user()
		data = self.valid_phone_data()
		data['number'] = 1
		self.client.force_login(user)

		url = reverse('profile:add_phone')
		response = self.client.get(url)
		form = AddPhonenumberForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(PHONE_INVALID_ERROR, form.errors['phonenumber'])
		

class PasswordValidationFormTest(BaseUserTest):
	def test_valid_form(self):
		user = self.new_user()
		self.client.force_login(user)

		url = reverse('profile:password_validation')
		data = {'password': VALID_PASS_1}
		response = self.client.get(url)
		form = PasswordValidationForm(response.wsgi_request, data=data)

		self.assertIs(form.is_valid(), True)


class UpdateProfileFormTest(BaseUserTest):
	def test_valid_form_first_last_email(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		updated_first_name = f"{data['first_name']}updated"
		updated_last_name = f"{data['last_name']}updated"
		updated_email = f"{data['email']}updated"

		data['first_name'] = updated_first_name
		data['last_name'] = updated_last_name
		data['email'] = updated_email

		url = reverse('profile:update_profile')		
		response = self.client.get(url)
		request = response.wsgi_request
		form = UpdateProfileForm(request, data=data)

		self.assertTrue(form.is_valid())
		form.save()

		self.assertEquals(request.user.first_name, updated_first_name)
		self.assertEquals(request.user.last_name, updated_last_name)
		self.assertEquals(request.user.email, updated_email)


class CodeVerificationFormTest(BaseUserTest):
	def test_form_invalid_empty_field(self):
		user = self.new_user()
		self.client.force_login(user)

		data = {'code': ''}
		url = reverse('profile:phone_verification')
		response = self.client.get(url)
		form = CodeVerificationForm(response.wsgi_request, data=data)

		self.assertFalse(form.is_valid())
		self.assertIn(EMPTY_CODE_ERROR, form.errors['code'])