class CustomError(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = ""


class UserExists(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = "user already exists"


class UserMissing(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = "user does not exist"


class PasswordRequirementError(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = "your password was not strong enough"


class MultipleUsersError(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = "multiple users exist"


class DiscordUuidUsed(Exception):
    def __init__(self, message, data=None):
        if data is None:
            data = {}
        print(F"error: `{message}` with data: `{data}`")
        self.message = message
        self.generic = "discord uuid was already used"
