import re

# Valid example test@gmail.com
def is_valid_email(email):
    pattern = r'([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+'
    return re.match(pattern, email) is not None