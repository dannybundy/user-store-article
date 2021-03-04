import json

from django.contrib import messages
from django.contrib.auth import logout
from django.urls import reverse


def deserialize_json(request):
	request.POST = request.POST.copy()
	json_data = json.loads(request.POST['json_data'])[1:]

	data = {}
	for element in json_data:
		request.POST[element['name']] = element['value']

	return request


def get_profile(request):
	email = request.session.get('email')
	phonenumber = request.session.get('phonenumber')

	profile = None
	if email is not None:
		profile = UserProfile.objects.get(email=email)
	
	elif phonenumber is not None:
		profile = UserProfile.objects.get(phonenumber=phonenumber)

	return profile


def check_for_lockout(request, profile):
	url = None
	if profile.temp_lockout():
		messages.warning(
			request,
			"You have attempted to log in too many times. Please try again later."
		)
		url = reverse('profile:login')
		logout(request)

	return url