import random, string


def create_ref_code():
	ref_code = ''.join(random.choices((string.ascii_lowercase + string.digits), k=20))
	return ref_code