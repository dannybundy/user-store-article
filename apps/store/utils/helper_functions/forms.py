from django.core.mail import send_mail
from django.template.loader import render_to_string


def send_order_email(order):
	order_description = order.get_order_description()
	description_list = order_description[0]
	description_str = order_description[1]

	ref_code = order.ref_code

	email_context =	{
		'order': order,
		'item_descriptions': description_list,
		'ref_code': ref_code
	}
	
	# Customer email
	html_customer_email = render_to_string(
		'store/order_customer_email.html',
		email_context,
	)

	send_mail(
		'Website Store: Order Summary',
		f"""Hi! You've purchased items:
		${order.get_price_total()} | {description_str} ({ref_code}) 
		- The Website Team
		""",
		'readapt-nutrition@readapt.com',
		['pilotdk13@gmail.com'],
		fail_silently=False,
		html_message=html_customer_email,
	)

	# Owner email
	html_admin_email = render_to_string(
		'store/order_admin_email.html',
		email_context,
	)

	send_mail(
		'Website Store: Someone bought some things',
		f"""{order.full_name} ({order.email}), ordered some things. Here they are:
		${order.get_price_total()} | {description_str} ({ref_code}).""",
		'readapt-nutrition@readapt.com',
		['pilotdk13@gmail.com'],
		fail_silently=False,
		html_message=html_admin_email,
	)