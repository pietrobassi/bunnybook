class ExpiredJwtToken(Exception):
    pass


class ExpiredJwtRefreshToken(Exception):
    pass


class InvalidatedJwtRefreshToken(Exception):
    pass


class LoginFailed(Exception):
    pass


class EmailAlreadyTaken(Exception):
    def __init__(self, msg="email already taken", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.field = "email"


class UsernameAlreadyTaken(Exception):
    def __init__(self, msg="username already taken", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
        self.field = "username"


class InvalidUsername(Exception):
    def __init__(self, msg="Username is invalid", *args, **kwargs):
        super().__init__(msg, *args, **kwargs)
