class Helpers:
    def __init__(self, settings, random, string):
        self.environ = settings
        self.random = random
        self.string = string

    def get_salt(self, salt_length):
        return ''.join(self.random.SystemRandom()
                       .choice(self.string.ascii_lowercase +
                               self.string.ascii_uppercase +
                               self.string.digits)
                       for _ in range(salt_length))
