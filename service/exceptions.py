
class UserFacingErrors(Exception):
    """" User-facing errors that can be displayed safely to the user. """
    pass

class RateLimitError(UserFacingErrors):
    pass

class AIServiceRequestError(UserFacingErrors):
    pass

class AIServiceAvailabilityError(UserFacingErrors):
    pass

