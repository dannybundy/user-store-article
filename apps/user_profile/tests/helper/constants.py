from django.urls import reverse


VALID_FIRST = "first"
VALID_LAST = "last84"
VALID_EMAIL = "email@g.com"
VALID_USER = "username"
VALID_PASS_1 = "password1!"
VALID_PASS_2 = "password2!"

PASS_LENGTH_ERROR = "Password is not at least 8 characters."
PASS_LETTER_ERROR = "Password does not contain a letter."
PASS_NUMBER_ERROR = "Password does not contain a number."
PASS_SPECIAL_CHAR_ERROR = "Password does not contain a special character."

PASS_FIRST_ERROR = "Password contains your first name."
PASS_LAST_ERROR = "Password contains your last name."
PASS_EMAIL_ERROR = "Password contains your email."
PASS_USER_ERROR = "Password contains your username."

USER_ERROR = "Username already exists in the system."
EMAIL_ERROR = "Email already exists in the system."


NEW_SAME_AS_OLD_ERROR = "Cannot set new password as old password. Please try again."
OLD_PASS_INCORRECT_ERROR = "Old password is incorrect. Please try again."

TEMP_LOCKOUT_ERROR = "You have attempted to log in too many times. Please try again later."

PHONE_LETTER_ERROR = "Use only numbers. Please try again."
EMPTY_PHONE_ERROR = "Please fill in blank fields."
EMPTY_CODE_ERROR = "Please enter a code."
EMAIL_AND_PHONE_ERROR = "Please choose either an email or phone number."

PHONE_EXISTS_ERROR = "Validated phone number already exists within the system."
PHONE_INVALID_ERROR = "Phone number was not valid. Please try again."



# Messages
REGISTRATION_SUCCESSFUL_MSG = "Successfully created account!"
PASS_CHANGED_MSG = "Your password has been changed."

LOGIN_TO_VIEW_MSG = "Log in to view content."
PASS_RESET_LINK_TEXT_MSG = "Reset Password Link has been sent to your phone."


temp = """
	Reset Password Link has been sent to your email. If it is is not in your inbox,
	check your spam mail.
	"""
PASS_RESET_LINK_EMAIL_MSG = ' '.join(temp.split())

USERNAME_TEXT_MSG = "Username has been sent to your phone."


temp = """
	Username has been sent to your email. If it is is not in your inbox, check your spam mail."""
USERNAME_EMAIL_MSG = ' '.join(temp.split())


NO_NEW_NUMBER_MSG = "You have no new number to verify."
CODE_RESENT_MSG = "Code has been resent to your phone."

PHONENUMBER_UPDATED_MSG = "<b>Phone number</b> has been updated. Check your phone for the verification code."
FIRST_NAME_UPDATED_MSG = "<b>First Name</b> updated."