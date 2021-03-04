from dateutil.relativedelta import *

from django.conf import settings
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from django.test import TestCase
from django.utils import timezone

from model_bakery import baker

from store.models import Customer
from user_profile.models import *


class UserProfileModelTest(TestCase):
	def test_create_user_profile_when_user_is_created(self):
		user = baker.make(User)
		profile_qs = UserProfile.objects.filter(user=user)
		profile = profile_qs[0]

		self.assertEqual(profile_qs.exists(), True)

	def test_signal_save_userprofile_when_user_is_saved(self):
		user = baker.make(User)
		profile = user.userprofile

		self.assertEqual(profile.first_name, user.first_name)
		self.assertEqual(profile.last_name, user.last_name)
		self.assertEqual(profile.email, user.email)

	def test_str(self):
		profile = baker.make(User).userprofile
		test_str = f"{profile.first_name} {profile.last_name}"

		self.assertEqual(str(profile), test_str)

	def test_save_customer_info(self):
		user = baker.make(User)
		customer = user.customer
		test_str = f"{user.first_name} {user.last_name}"

		self.assertEqual(customer.full_name, test_str)
		self.assertEqual(customer.email, user.email)

	def test_save_slugify(self):
		profile = baker.make(User).userprofile
		test_slug = slugify(profile.user.username)

		self.assertEqual(profile.slug, test_slug)

	def test_add_attempt(self):
		profile = baker.make(User).userprofile
		profile.add_attempt()

		self.assertEqual(profile.login_attempt, 1)

	def test_add_lockout(self):
		profile = baker.make(User).userprofile
		profile.add_lockout()

		self.assertEqual(profile.login_lockout, 1)


	def create_profile(self, attempt, lockout):
		profile = baker.make(User).userprofile
		profile.login_attempt = attempt
		profile.login_lockout = lockout
		profile.save()

		return profile

	def test_reset_values(self):
		profile = self.create_profile(5, 2)
		profile.reset_values()

		self.assertEqual(profile.login_attempt, 0)
		self.assertEqual(profile.login_lockout, 0)

	def test_temp_lockout(self):
		profile = self.create_profile(5, 0)
		self.assertTrue(profile.temp_lockout())

	def test_perm_lockout(self):
		profile = self.create_profile(5, 2)
		self.assertTrue(profile.perm_lockout())

	def test_lockout_over(self):
		profile = self.create_profile(5, 0)
		profile.login_attempt_time = timezone.now() - relativedelta(minutes=LOCKOUT_WAIT_TIME+1)
		profile.save()

		self.assertTrue(profile.lockout_over())


	def test_validation_required(self):
		last_login = timezone.now() - relativedelta(hours=VALIDATION_TIME_LIMIT+1)
		user = baker.make(User, last_login=last_login)

		self.assertTrue(user.userprofile.validation_required())

	def test_allow_send_msg(self):
		send_msg_time = timezone.now() - relativedelta(minutes=RESEND_WAIT_TIME+1)
		
		profile = baker.make(User).userprofile
		profile.send_msg_time = send_msg_time
		profile.save()

		self.assertTrue(profile.allow_send_msg())

	def test_set_phonenumber(self):
		phonenumber = settings.TRIAL_NUMBER
		service_sid = 'service_sid'

		profile = baker.make(User).userprofile
		profile.set_phonenumber(phonenumber, service_sid)

		self.assertEqual(profile.phonenumber, phonenumber)
		self.assertEqual(profile.service_sid, service_sid)
		self.assertFalse(profile.verified_number)

	def test_verify_phonenumber(self):
		profile = baker.make(User).userprofile
		profile.verify_phonenumber()
		self.assertTrue(profile.verified_number)

	def test_disable_account(self):
		user = baker.make(User)
		user.userprofile.disable_account()
		self.assertFalse(user.is_active)


class UserStyleModelTest(TestCase):
	def test_str(self):
		user_style = baker.make(UserStyle)
		self.assertEqual(str(user_style), "CSS")