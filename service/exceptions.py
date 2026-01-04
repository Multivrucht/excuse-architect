
class UserFacingErrors(Exception):
    """" User-facing errors that can be displayed safely to the user. """
    status_code: int = 500

class RateLimitError(UserFacingErrors):
    status_code = 429

class AIServiceRequestError(UserFacingErrors):
    status_code = 502

class AIServiceAvailabilityError(UserFacingErrors):
    status_code = 503
