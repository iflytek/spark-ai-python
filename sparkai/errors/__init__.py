"""Errors that can be raised by this SDK"""


class SparkAIClientError(Exception):
    """Base class for Client errors"""


class BotUserAccessError(SparkAIClientError):
    """Error raised when an 'xoxb-*' token is
    being used for a SparkAI API method that only accepts 'xoxp-*' tokens.
    """


class SparkAIRequestError(SparkAIClientError):
    """Error raised when there's a problem with the request that's being submitted."""


class SparkAIApiError(SparkAIClientError):
    """Error raised when SparkAI does not send the expected response.

    Attributes:
        response (SparkAIResponse): The SparkAIResponse object containing all of the data sent back from the API.

    Note:
        The message (str) passed into the exception is used when
        a user converts the exception to a str.
        i.e. str(SparkAIApiError("This text will be sent as a string."))
    """

    def __init__(self, message, response):
        msg = f"{message}\nThe server responded with: {response}"
        self.response = response
        super(SparkAIApiError, self).__init__(msg)


class SparkAITokenRotationError(SparkAIClientError):
    """Error raised when the oauth.v2.access call for token rotation fails"""

    api_error: SparkAIApiError

    def __init__(self, api_error: SparkAIApiError):
        self.api_error = api_error


class SparkAIClientNotConnectedError(SparkAIClientError):
    """Error raised when attempting to send messages over the websocket when the
    connection is closed."""


class SparkAIObjectFormationError(SparkAIClientError):
    """Error raised when a constructed object is not valid/malformed"""


class SparkAIClientConfigurationError(SparkAIClientError):
    """Error raised because of invalid configuration on the client side:
    * when attempting to send messages over the websocket when the connection is closed.
    * when external system (e.g., Amazon S3) configuration / credentials are not correct
    """


class SparkAIConnectionError(ConnectionError):
    def __init__(self, error_code, message):
        self.error_code = error_code
        self.message = message
        super().__init__(message)