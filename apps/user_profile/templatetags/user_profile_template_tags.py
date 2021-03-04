from django import template
from user_profile.models import *

register = template.Library()

@register.filter(name='profile_slug')
def profile_slug(user):
	if user.is_authenticated:
		profile_slug = UserProfile.objects.get(user=user).slug
	else:
		# Not logged in
		profile_slug = None

	return profile_slug


@register.filter(name='show_verify')
def verified_number(user):
	val=True
	if user.is_authenticated:
		profile = UserProfile.objects.get(user=user)
		verified_number = profile.verified_number
		# If already verified, return False (hides button)
		if verified_number or not profile.phonenumber:
			val = False
	# If not verified yet, return True (shows button)
		else:
			val = True

	return val



@register.filter(name="website")
def get_website_style(obj):
	user_style = UserStyle.objects.all()
	if len(user_style)>0:
		return user_style[0].website

	return None

@register.filter(name="admin_page")
def get_admin_page_style(obj):
	user_style = UserStyle.objects.all()
	if len(user_style)>0:
		return user_style[0].admin_page

	return None