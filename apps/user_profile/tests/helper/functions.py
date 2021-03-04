import datetime

from dateutil.relativedelta import *
from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone
from model_bakery import baker

from user_profile.forms import *
from user_profile.models import *
from .constants import *


class BaseUserTest(TestCase):
	def valid_user_data(self):
		data = {
			'first_name': VALID_FIRST,
			'last_name': VALID_LAST,
			'email': VALID_EMAIL,
			'username': VALID_USER,
			'password': VALID_PASS_1,
		}
		return data

	def valid_phone_data(self):
		data = {
			'country_code': 'US',
			'area_code': '828',
			'number': '3988580',
		}
		return data


	def new_user(self):
		data = self.valid_user_data()
		user = baker.make(
			User,
			first_name=data['first_name'],
			last_name=data['last_name'],
			email=data['email'],
			username=data['username'],
		)
		user.set_password(data['password'])
		user.save()

		send_msg_time = timezone.now() - relativedelta(minutes=RESEND_WAIT_TIME+1)
		
		profile = user.userprofile
		profile.send_msg_time = send_msg_time
		profile.save()

		return user

	def attach_phonenumber(self, user, data):
		form = PhonenumberForm(data=data)
		form.is_valid()
		phonenumber = form.cleaned_data.get('phonenumber')

		profile = user.userprofile
		profile.phonenumber = phonenumber
		profile.verified_number = True
		profile.save()

		return profile