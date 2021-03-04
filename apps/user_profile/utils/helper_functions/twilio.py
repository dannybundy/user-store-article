from django.conf import settings

from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client

account_sid = settings.ACCOUNT_SID
auth_token = settings.AUTH_TOKEN


def twilio_auth(profile, body):
	try:
		client = Client(account_sid, auth_token)
		client.messages.create(
			to=f"{profile.phonenumber}",
			from_=settings.TRIAL_NUMBER,
			body=body
		)
	except TwilioRestException as e:
		raise e


def twilio_send_code(profile, phonenumber):
	try:
		client = Client(account_sid, auth_token)
		service = client.verify.services.create(
			friendly_name='name',
		)

		verification = client.verify \
		.services(service.sid) \
		.verifications \
		.create(to=str(phonenumber), channel='sms')
		profile.set_phonenumber(phonenumber, service.sid)
		return True

	except TwilioRestException as e:
		return False


def twilio_verify_code(profile, code):
	try:
		client = Client(account_sid, auth_token)
		verification_check = client.verify \
		.services(profile.service_sid) \
		.verification_checks \
		.create(to=str(profile.phonenumber), code=code)
	
		if verification_check.status == 'approved':
			profile.verify_phonenumber()
			return True

	except TwilioRestException as e:
		pass

	return False