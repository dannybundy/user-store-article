from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils import timezone

from phonenumber_field.modelfields import PhoneNumberField

from store.models import Customer


MAX_LOGIN_ATTEMPT = 4
MAX_LOCKOUT = 1

LOCKOUT_WAIT_TIME = 15
RESEND_WAIT_TIME = 15
VALIDATION_TIME_LIMIT = 1

class UserProfile(models.Model):
	user = models.OneToOneField(User, related_name='userprofile', on_delete=models.CASCADE, blank=True, null=True)
	first_name = models.CharField(max_length=100)
	last_name = models.CharField(max_length=100)
	email = models.EmailField(max_length=50)
	slug = models.SlugField(unique=True)
	
	login_attempt = models.IntegerField(default=0)
	login_attempt_time = models.DateTimeField(default=timezone.now)
	login_lockout = models.IntegerField(default=0)
	send_msg_time = models.DateTimeField(default=timezone.now)

	phonenumber = PhoneNumberField(null=True, blank=True, unique=True)
	service_sid = models.CharField(max_length=50, null=True, blank=True)
	verified_number = models.BooleanField(default=False)

	def __str__(self):
		string = ''
		if not self.user.is_active:
			string = ' (deactivated)'
		return f"{self.first_name} {self.last_name}{string}"

	def save(self, *args, **kwargs):
		self.first_name = self.user.first_name 
		self.last_name = self.user.last_name
		self.email = self.user.email

		if self.user is not None:
			self.slug = self.slug or slugify(self.user.username)

		customer_qs = Customer.objects.filter(user=self.user)
		if customer_qs.exists():
			customer_qs[0].save()


		super().save(*args, **kwargs)


	# Logging in
	def add_attempt(self):
		self.login_attempt += 1
		self.login_attempt_time = timezone.now()
		self.save()

		return self

	def add_lockout(self):
		self.login_attempt = 0
		self.login_lockout += 1
		self.save()

		return self

	def reset_values(self):
		self.login_attempt = 0
		self.login_lockout = 0
		self.login_attempt_time = timezone.now()
		self.save()

		self.user.last_login = timezone.now()
		self.user.save()

		return self

	def temp_lockout(self):
		return self.login_attempt > MAX_LOGIN_ATTEMPT

	def perm_lockout(self):
		return self.login_lockout > MAX_LOCKOUT

	def lockout_over(self):
		time_dif = (timezone.now() - self.login_attempt_time).total_seconds() / 60  #minutes
		return time_dif > LOCKOUT_WAIT_TIME


	# Password validation
	def validation_required(self):
		time_dif = (timezone.now() - self.user.last_login).total_seconds() / 3600  #hours
		return time_dif > VALIDATION_TIME_LIMIT


	# Requesting password reset link or username
	def send_msg_time_dif(self):
		return (timezone.now() - self.send_msg_time).total_seconds()

	def send_msg_wait_time(self):
		return int(RESEND_WAIT_TIME - self.send_msg_time_dif())

	def allow_send_msg(self):
		return self.send_msg_time_dif() > RESEND_WAIT_TIME

	def is_showcase_user(self):
		return self.user.username == "Al"


	# Updating profile
	def set_phonenumber(self, phonenumber, service_sid):
		self.phonenumber = phonenumber
		self.service_sid = service_sid
		self.verified_number = False
		self.save()

	def verify_phonenumber(self):
		self.verified_number = True
		self.save()

	def disable_account(self):
		self.reset_values()
		self.user.is_active = False
		self.user.save()


def userprofile_reciever(sender, instance, created, *args, **kwargs):
	if created:
		userprofile = UserProfile.objects.create(user=instance)
post_save.connect(userprofile_reciever, sender=User)


@receiver(post_save, sender=User, dispatch_uid="update_userprofile")
def update_userprofile(sender, instance, **kwargs):
	instance.userprofile.save()


class UserStyle(models.Model):
	website = models.TextField()
	admin_page = models.TextField()

	def __str__(self):
		return "CSS"