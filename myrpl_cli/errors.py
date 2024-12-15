class MyRPLError(BaseException):
	"""Generic error"""


class NotMyRPLDirectoryError(MyRPLError):
	"""Not in a myrpl directory error"""


class NotMyRPLActivityDirectoryError(NotMyRPLDirectoryError):
	"""Not in a myrpl activity directory error"""


class AuthError(BaseException):
	"""Generic authentication error"""


class MissingCredentialsError(AuthError):
	"""Missing credentials error"""
