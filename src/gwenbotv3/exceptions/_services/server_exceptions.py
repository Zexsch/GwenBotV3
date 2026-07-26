class ServerError(Exception):
    pass


class ServerIdNotGivenError(ServerError):
    pass


class ServerNotFoundError(ServerError):
    pass
