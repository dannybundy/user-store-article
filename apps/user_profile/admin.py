from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, Avg

from rangefilter.filter import DateRangeFilter, DateTimeRangeFilter

from user_profile.models import *


class UserProfileInline(admin.StackedInline):
	model = UserProfile
	verbose_name = 'Profile'
	verbose_name_plural = 'Personal Info'
	fields = [
		'phonenumber',
		'service_sid',
		'verified_number',

		'login_attempt',
		'login_attempt_time',
		'login_lockout',
		'send_msg_time',
	]
	# readonly_fields = [
	# 	'phonenumber',
	# 	'service_sid',
	# 	'verified_number',

	# 	# 'login_attempt',
	# 	'login_attempt_time',
	# 	'send_msg_time',
	# ]

	# def has_add_permission(self, request, obj=None):
	# 	return False

	# def has_delete_permission(self, request, obj=None):
	# 	return False

class UserAdmin(admin.ModelAdmin):
	inlines = [UserProfileInline,]
	fields = [
		'username', 'first_name', 'last_name',
		'email', 'date_joined',
		'user_permissions', 'is_staff',
		'is_superuser', 'is_active',
		'last_login'
	]
	readonly_fields = [
		'username', 'first_name', 'last_name',
		'email', 'date_joined',
	]
	list_display = [
		'username',
		'full_name',
		'email',
		'phonenumber',
	]
	search_fields = [
		'username',
		'first_name',
		'last_name',
		'email',
		'phonenumber',
	]

	# def has_add_permission(self, request, obj=None):
	# 	return False

	# def has_delete_permission(self, request, obj=None):
	# 	return False

	def full_name(self, obj):
		return f"{obj.first_name} {obj.last_name}"
	
	def phonenumber(self, obj):
		return obj.userprofile.phonenumber


class UserStyleAdmin(admin.ModelAdmin):
	verbose_name_plural = 'User Style'

	def has_add_permission(self, request):
		return False

	def has_delete_permission(self, request, obj=None):
		return False


admin.site.unregister(Group)
admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.register(UserStyle, UserStyleAdmin)