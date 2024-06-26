from keyrings.cryptfile.cryptfile import CryptFileKeyring

SERVICE_NAME = "myrpl_cli"


class CredentialManager:
	def __init__(self):
		self.kr = CryptFileKeyring()

	def get_stored_credentials(self):
		username = self.kr.get_password(SERVICE_NAME, "username")
		password = self.kr.get_password(SERVICE_NAME, "password")
		return username, password

	def store_credentials(self, username, password):
		self.kr.set_password(SERVICE_NAME, "username", username)
		self.kr.set_password(SERVICE_NAME, "password", password)

	def get_stored_token(self):
		return self.kr.get_password(SERVICE_NAME, "token")

	def store_token(self, token):
		self.kr.set_password(SERVICE_NAME, "token", token)
