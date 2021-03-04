import datetime, json

from dateutil.relativedelta import *

from django.contrib.messages import get_messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.core import mail
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from model_bakery import baker
from twilio.rest import Client
from unittest import mock

from user_profile.models import *
from .helper.constants import *
from .helper.functions import *


class CustomRegistrationViewTest(BaseUserTest):
	def test_redirect_logged_in_user(self):
		user = baker.make(User)
		self.client.force_login(user)
		url = reverse('profile:register')
		response = self.client.get(url)

		test_redirect_url = reverse('profile:home')

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, test_redirect_url)

	def test_registration_successful_success_url(self):
		url = reverse('profile:register')
		data = self.valid_user_data()
		response = self.client.post(url, data=data)
		message_list = list(get_messages(response.wsgi_request))

		test_redirect_url = reverse('profile:login')
		total_user_count = User.objects.all().count()

		self.assertEqual(total_user_count, 1)
		self.assertIn(REGISTRATION_SUCCESSFUL_MSG, str(message_list[0]))
		self.assertRedirects(response, test_redirect_url)

	# unable to convert post request data into json
	# def test_registration_unsuccessful_ajax_validation(self):
	# 	baker.make(User, email=VALID_EMAIL)
	# 	form_data = self.valid_user_data()


	# 	array = []
	# 	for field, value in form_data.items():
	# 		name = json.dumps("name" + ":" + field)
	# 		value = json.dumps("value" + ":" + value)

	# 		array.append({name, value})


		# for val in array:
		# 	array[i].replace("\'", "\"")

		# ajax_data = {'json_data': [f'{array}']}
		# print(ajax_data)


		# url = reverse('profile:register')
		# response = self.client.post(
		# 	url,
		# 	data=ajax_data,
		# 	# content_type='application/json',
		# 	HTTP_X_REQUESTED_WITH='XMLHttpRequest',
		# )

		# form = CustomRegistrationForm(response.wsgi_request, data=form_data)
		# form.is_valid()

		# data = json.loads(response.content)
		
		# self.assertEqual(data, {'error_list': form.errors })


class CustomAuthenticationViewTest(BaseUserTest):
	def test_authentication_approved_with_first_login_redirect_to_add_phone_view(self):
		user = self.new_user()
		data = {'username': user.username, 'password': VALID_PASS_1}
		url = reverse('profile:login')
		response = self.client.post(url, data=data)
		test_redirect_url = reverse('profile:add_phone')

		self.assertEqual(response.wsgi_request.user, user)
		self.assertRedirects(response, test_redirect_url)

	def test_authentication_approved_with_ajax_json_data(self):
		user = self.new_user()
		ajax_data = {'username': user.username, 'password': VALID_PASS_1}
		url = reverse('profile:login')

		response = self.client.post(
			url,
			data=ajax_data,
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		data = json.loads(response.content)
		new_url = reverse_lazy('profile:add_phone')

		self.assertEqual(data, {'url': new_url})


	def test_authentication_not_approved_with_ajax_json_data(self):
		user = self.new_user()
		ajax_data = {'username': user.username, 'password': VALID_PASS_2}
		url = reverse('profile:login')

		response = self.client.post(
			url,
			data=ajax_data,
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		data = json.loads(response.content)

		form = CustomAuthenticationForm(response.wsgi_request, data=ajax_data)
		form.is_valid()

		self.assertEqual(data, {'error_list': form.errors})


class CustomPasswordChangeViewTest(BaseUserTest):
	def test_redirect_anonymous_user(self):
		url = reverse('profile:password_change')
		response = self.client.get(url)
		test_redirect_url = reverse('profile:login')

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, test_redirect_url)

	def test_password_change_successful(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		old_password = data['password']

		data['old_password'] = old_password
		data['password'] = VALID_PASS_2

		url = reverse('profile:password_change')
		response = self.client.post(url, data=data)
		request = response.wsgi_request
		message_list = list(get_messages(request))
		test_redirect_url = reverse('profile:login')

		self.assertIn(PASS_CHANGED_MSG, str(message_list[0]))
		self.assertTrue(request.user.is_anonymous)
		self.assertRedirects(response, test_redirect_url)

	def test_temp_lockout(self):
		user = self.new_user()
		self.client.force_login(user)

		UserProfile.objects.filter(user=user).update(login_attempt=4)

		data = self.valid_user_data()
		data['old_password'] = VALID_PASS_2
		data['password'] = VALID_PASS_2


		url = reverse('profile:password_change')
		response = self.client.post(url, data=data)
		request = response.wsgi_request
		message_list = list(get_messages(request))
		test_redirect_url = reverse('profile:login')

		self.assertIn(TEMP_LOCKOUT_ERROR, str(message_list[0]))
		self.assertTrue(request.user.is_anonymous)
		self.assertRedirects(response, test_redirect_url)


class CustomPasswordResetViewTest(BaseUserTest):
	def test_check_email(self):
		user = self.new_user()
		data = {'email': user.email}

		url = reverse('profile:password_reset_request')
		response = self.client.post(url, data=data)
		message_list = list(get_messages(response.wsgi_request))
		test_subject_str = "Website Password Reset"
		test_redirect_url = reverse('profile:login')

		temp = str(message_list[0])
		actual_msg = ' '.join(temp.split())

		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, test_subject_str)
		self.assertIn(PASS_RESET_LINK_EMAIL_MSG, actual_msg)
		self.assertRedirects(response, test_redirect_url)

	def test_send_text(self):
		user = self.new_user()
		data = self.valid_phone_data()
		self.attach_phonenumber(user, data)

		url = reverse('profile:password_reset_request')
		response = self.client.post(url, data=data)
		message_list = list(get_messages(response.wsgi_request))
		test_redirect_url = reverse('profile:login')

		self.assertIn(PASS_RESET_LINK_TEXT_MSG, str(message_list[0]))
		self.assertRedirects(response, test_redirect_url)


class RecoverUsernameViewTest(BaseUserTest):
	def test_check_email(self):
		user = self.new_user()
		data = {'email': user.email}

		url = reverse('profile:recover_username')
		response = self.client.post(url, data=data)
		message_list = list(get_messages(response.wsgi_request))
		test_subject_str = "Recover Username"
		test_redirect_url = reverse('profile:login')

		temp = str(message_list[0])
		actual_msg = ' '.join(temp.split())

		self.assertEqual(len(mail.outbox), 1)
		self.assertEqual(mail.outbox[0].subject, test_subject_str)
		self.assertIn(USERNAME_EMAIL_MSG, actual_msg)
		self.assertRedirects(response, test_redirect_url)

	def test_send_text(self):
		user = self.new_user()
		data = self.valid_phone_data()
		self.attach_phonenumber(user, data)

		url = reverse('profile:recover_username')
		response = self.client.post(url, data=data)
		message_list = list(get_messages(response.wsgi_request))
		test_redirect_url = reverse('profile:login')

		self.assertIn(USERNAME_TEXT_MSG, str(message_list[0]))
		self.assertRedirects(response, test_redirect_url)


class PasswordValidationViewTest(BaseUserTest):
	def test_redirect_if_validation_not_required(self):
		user = self.new_user()
		self.client.force_login(user)

		url = reverse('profile:password_validation')
		response = self.client.get(url)
		test_redirect_url = reverse('profile:profile')

		self.assertEqual(response.status_code, 302)
		self.assertRedirects(response, test_redirect_url)

	def test_validation_successful(self):
		user = self.new_user()
		self.client.force_login(user)
		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+2) 
		user.last_login = last_login
		user.save()

		data = {'password': VALID_PASS_1}
		url = reverse('profile:password_validation')
		response = self.client.post(url, data=data)
		request = response.wsgi_request
		test_redirect_url = reverse('profile:profile')

		self.assertIsNot(request.user.last_login, last_login)
		self.assertRedirects(response, test_redirect_url)


class AjaxPasswordValidationViewTest(BaseUserTest):
	def test_password_validation_required_too_many_login_attempts_ajax_json_data(self):
		user = self.new_user()
		self.client.force_login(user)
		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+2) 
		user.last_login = last_login
		user.save()

		profile = user.userprofile
		profile.login_attempt = 4
		profile.save()

		new_url = reverse('profile:update_profile')
		ajax_data = {'update_option': new_url, 'password': VALID_PASS_2}

		url = reverse('profile:ajax_password_validation')
		response = self.client.post(
			url,
			data=ajax_data,
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		data = json.loads(response.content)

		self.assertEqual(data, {'refresh': "Too many attempts."} )

	def test_password_validation_required_invalid_password_ajax_json_data(self):
		user = self.new_user()
		self.client.force_login(user)
		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+2) 
		user.last_login = last_login
		user.save()

		new_url = reverse('profile:update_profile')
		ajax_data = {'update_option': new_url, 'password': VALID_PASS_2}

		url = reverse('profile:ajax_password_validation')
		response = self.client.post(
			url,
			data=ajax_data,
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		data = json.loads(response.content)

		form = PasswordValidationForm(response.wsgi_request, data=ajax_data)
		form.is_valid()

		self.assertEqual(data, {'error_list': form.errors})

	def test_password_validation_required_valid_password_ajax_json_data(self):
		user = self.new_user()
		self.client.force_login(user)
		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+2) 
		user.last_login = last_login
		user.save()

		new_url = reverse('profile:update_profile')
		ajax_data = {'update_option': new_url, 'password': VALID_PASS_1}

		url = reverse('profile:ajax_password_validation')
		response = self.client.post(
			url,
			data=ajax_data,
			HTTP_X_REQUESTED_WITH='XMLHttpRequest'
		)
		data = json.loads(response.content)

		self.assertEqual(data, {'refresh': 'Correct info.'})


class AddPhoneViewTest(BaseUserTest):
	def test_redirect_not_first_login(self):
		user = self.new_user()
		self.client.force_login(user)

		url = reverse('profile:add_phone')
		response = self.client.get(url)
		message_list = list(get_messages(response.wsgi_request))
		test_redirect_url = reverse('profile:update_profile')

		self.assertRedirects(response, test_redirect_url)

	def test_phonenumber_added(self):
		user = self.new_user()
		self.client.force_login(user)

		session = self.client.session
		session['first_login'] = "first time logging in"
		session.save()

		url = reverse('profile:add_phone')
		data = self.valid_phone_data()
		response = self.client.post(url, data=data)
		request = response.wsgi_request

		self.assertIsNot(request.user.userprofile.phonenumber, None)

	def test_add_phonenumber_later_redirect(self):
		user = self.new_user()
		self.client.force_login(user)

		session = self.client.session
		session['first_login'] = "first time logging in"
		session.save()

		url = reverse('profile:add_phone')
		data = {'later': True}
		response = self.client.post(url, data=data)
		test_redirect_url = reverse('profile:home')

		self.assertRedirects(response, test_redirect_url)


class PhoneVerificationViewTest(BaseUserTest):
	def test_redirect_no_new_phonenumber_to_verify(self):
		user = self.new_user()
		self.client.force_login(user)

		url = reverse('profile:phone_verification')
		response = self.client.get(url)
		test_redirect_url = reverse('profile:home')

		message_list = list(get_messages(response.wsgi_request))
		temp = str(message_list[0])
		actual_msg = ' '.join(temp.split())

		self.assertEqual(NO_NEW_NUMBER_MSG, actual_msg)
		self.assertRedirects(response, test_redirect_url)

	def test_twilio_resend_code(self):
		user = self.new_user()
		self.client.force_login(user)
		
		phone_data = self.valid_phone_data()
		self.attach_phonenumber(user, phone_data)
		profile = user.userprofile
		profile.verified_number = False
		profile.save()

		url = reverse('profile:phone_verification')
		data = {'resend_code': True}
		response = self.client.post(url, data=data)

		message_list = list(get_messages(response.wsgi_request))
		temp = str(message_list[0])
		actual_msg = ' '.join(temp.split())

		self.assertEqual(CODE_RESENT_MSG, actual_msg)

	# @mock.patch('client.verify.services.verification_checks.create')
	# def test_twilio_code_verified(self, code_verified):
	# 	code_verified.return_value.stauts = 'approved'
	# 	print(code_verified)

	# 	user = self.new_user()
	# 	self.client.force_login(user)
		
	# 	phone_data = self.valid_phone_data()
	# 	self.attach_phonenumber(user, phone_data)
	# 	profile = user.userprofile
	# 	profile.verified_number = False
	# 	profile.save()

	# 	url = reverse('profile:phone_verification')
	# 	data = {'code': }
	# 	response = self.client.post(url, data=data)

	# 	message_list = list(get_messages(response.wsgi_request))
	# 	temp = str(message_list[0])
	# 	actual_msg = ' '.join(temp.split())

	# 	self.assertEqual(PHONENUMBER_UPDATED_MSG, actual_msg)


class ProfileViewTest(BaseUserTest):
	def test_verify_password_close_to_context_if_password_validation_is_required(self):
		user = self.new_user()
		self.client.force_login(user)

		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+1)
		user.last_login = last_login
		user.save()

		url = reverse('profile:profile')
		response = self.client.get(url)

		self.assertIn('verify_password', response.context)


class UpdateProfileViewTest(BaseUserTest):
	def test_disable_account(self):
		user = self.new_user()
		self.client.force_login(user)

		url = reverse('profile:update_profile')
		data = {'disable': True}
		response = self.client.post(url, data=data)

		user = User.objects.get(pk=user.pk)
		test_redirect_url = reverse('profile:login')

		self.assertFalse(user.is_active)
		self.assertRedirects(response, test_redirect_url)

	def test_update_profile_succesful(self):
		user = self.new_user()
		self.client.force_login(user)

		data = self.valid_user_data()
		updated_first_name = f"{data['first_name']}updated"
		data['first_name'] = updated_first_name


		url = reverse('profile:update_profile')		
		response = self.client.post(url, data)
		request = response.wsgi_request

		message_list = list(get_messages(request))
		temp = str(message_list[0])
		actual_msg = ' '.join(temp.split())

		test_redirect_url = reverse('profile:profile')

		self.assertEquals(request.user.first_name, updated_first_name)
		self.assertEqual(FIRST_NAME_UPDATED_MSG, actual_msg)
		self.assertRedirects(response, test_redirect_url)