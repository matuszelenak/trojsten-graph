import random
import string


def random_token():
    return ''.join(random.sample(string.ascii_uppercase + string.ascii_lowercase + string.digits, 20))


def snake_to_camel(s):
    def capitalizer(words):
        yield words[0].lower()
        for word in words[1:]:
            yield word.lower().capitalize()

    return ''.join(capitalizer(s.split('_')))
