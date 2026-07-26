class UserError(Exception):
    pass


class UserIdOrNameNotGivenError(UserError):
    pass


class UserNotFoundError(UserError):
    pass


class UserIsAnonymisedError(UserError):
    pass


class UserNotAnonymisedError(UserError):
    pass
