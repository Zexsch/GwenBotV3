class PrivacyError(Exception):
    pass


class UserAlreadyPrivateError(PrivacyError):
    pass


class UserNotPrivateError(PrivacyError):
    pass
