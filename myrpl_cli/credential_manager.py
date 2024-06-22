# credential_manager.py

from keyrings.cryptfile.cryptfile import CryptFileKeyring

# TODO support other keyrings
kr = CryptFileKeyring()

SERVICE_NAME = 'myrpl_cli'

class CredentialManager:

    def get_stored_credentials(self):
        username = kr.get_password(SERVICE_NAME, 'username')
        password = kr.get_password(SERVICE_NAME, 'password')
        return username, password

    def store_credentials(self, username, password):
        kr.set_password(SERVICE_NAME, 'username', username)
        kr.set_password(SERVICE_NAME, 'password', password)

    def get_stored_token(self):
        token = kr.get_password(SERVICE_NAME, 'token')
        return token

    def store_token(self, token):
        kr.set_password(SERVICE_NAME, 'token', token)
