def hide_admin_btns(extra_context):
	extra_context['show_save_and_continue'] = False
	extra_context['show_save_and_add_another'] = False
	extra_context['close'] = False
	return extra_context


def get_user_or_guest(obj):
	if obj is not None:
		if obj.customer.user is not None:
			return obj.customer.user.username

		return f"Guest {obj.customer.guest_num}"