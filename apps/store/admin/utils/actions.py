# Item
def make_active(modeladmin, request, queryset):
	queryset.update(is_active=True)
make_active.short_description = "Mark selected items as active"

def make_inactive(modeladmin, request, queryset):
	queryset.update(is_active=False)
make_inactive.short_description = "Mark selected items as inactive"



# Order
def delivered(modeladmin, request, queryset):
	queryset.update(delivered=True)
delivered.short_description = "Mark selected orders as delivered"

def undelivered(modeladmin, request, queryset):
	queryset.update(delivered=False)
undelivered.short_description = "Mark selected orders as not delivered"


def recieved(modeladmin, request, queryset):
	queryset.update(recieved=True)
recieved.short_description = "Mark selected orders as recieved"

def unrecieved(modeladmin, request, queryset):
	queryset.update(recieved=False)
unrecieved.short_description = "Mark selected orders as not recieved"


def refund(modeladmin, request, queryset):
	queryset.update(is_active=True)
refund.short_description = "Mark selected items as refunded"

def unrefund(modeladmin, request, queryset):
	queryset.update(is_active=True)
unrefund.short_description = "Mark selected items as not refunded"


def cancel(modeladmin, request, queryset):
	queryset.update(cancelled=True)
cancel.short_description = "Mark selected orders as cancelled"

def uncancel(modeladmin, request, queryset):
	queryset.update(cancelled=False)
uncancel.short_description = "Mark selected orders as not cancelled"
