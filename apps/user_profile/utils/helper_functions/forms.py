import random, string

def random_string(k):
	token = ''.join(random.choices((string.ascii_lowercase + string.digits), k=k))
	return token