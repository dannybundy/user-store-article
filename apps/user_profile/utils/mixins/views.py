import json

from django.http import JsonResponse
from django.views.generic import FormView

from user_profile.forms import PasswordValidationForm



class RequestFormMixin:
	def get_form_kwargs(self):
		kwargs = super().get_form_kwargs()
		kwargs.update({'request': self.request})
		return kwargs



def json_response_with_errors(form):
	data = {'error_list': form.errors}
	return JsonResponse(data, status=200)


class AjaxValidateFormMixin:
	def form_valid(self, form):		
		# Returns empty error dict to front end to enable submit button
		if self.request.is_ajax():
			return json_response_with_errors(form)
		
		form.save()
		return super().form_valid(form)

	def form_invalid(self, form):
		# Ajax validation
		if self.request.is_ajax():
			return json_response_with_errors(form)

		return super().form_invalid(form)


class ChangePasswordFormMixin(RequestFormMixin, AjaxValidateFormMixin):
	def post(self, *args, **kwargs):
		profile = self.profile
		self.request.POST = self.request.POST.copy()

		self.request.POST['email'] = profile.email
		self.request.POST['username'] = profile.user.username
		self.request.POST['first_name'] = profile.first_name
		self.request.POST['last_name'] = profile.last_name

		return super().post(self.request, **kwargs)



class VerifyPasswordContextMixin:
	def get_context_data(self, **kwargs):
		context = super().get_context_data(**kwargs)
		context_name = "verify_password"

		if self.profile.validation_required():
			context[context_name] = PasswordValidationForm(self.request)

		return context