class NoDeleteMixin:
	def has_delete_permission(self, request, obj=None):
		return False

class NoAddDeleteMixin(NoDeleteMixin):
	def has_add_permission(self, request, obj=None):
		return False

class NoAddChangeDeleteMixin(NoAddDeleteMixin):
	def has_change_permission(self, request, obj=None):
		return False