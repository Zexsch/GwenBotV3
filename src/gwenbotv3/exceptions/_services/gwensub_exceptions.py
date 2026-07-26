class GwensubError(Exception):
    pass


class UserIsSubscribedError(GwensubError):
    pass


class UserNotSubscribedError(GwensubError):
    pass


class UserIsBlacklistedError(GwensubError):
    pass


class UserNotBlacklistedError(GwensubError):
    pass
