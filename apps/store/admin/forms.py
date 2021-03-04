from django import forms
from django.contrib import messages

from store.models import *


# class CalendarForm(forms.Form):
# 	date__gte = forms.DateField(
# 		required=False,
# 		widget=forms.widgets.DateInput(
# 			attrs={
# 				'type': 'date',
# 			},
# 		)
# 	)
# 	date__lte = forms.DateField(
# 		required=False,
# 		widget=forms.widgets.DateInput(
# 			attrs={
# 				'type': 'date',
# 			},
# 		)
# 	)
# 	def __init__(self, request, *args, **kwargs):
# 		super().__init__(*args, **kwargs)
# 		self.request = request

# 		date_gte = request.GET.get('date__gte', None)
# 		date_lte = request.GET.get('date__lte', None)

# 		self.fields['date__gte'].initial = date_gte
# 		self.fields['date__lte'].initial = date_lte

# 	def clean(self):
# 		clean = self.cleaned_data
# 		date_gte = clean.get('date__gte', None)
# 		date_lte = clean.get('date__lte', None)

# 		if (date_gte and date_lte) is not None:
# 			if (date_lte - date_gte).days < 0:
# 				messages.warning(self.request, "Pick valid dates")
# 				raise forms.ValidationError("Pick valid dates")

# 		return clean