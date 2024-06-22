import json
import requests
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder

BASE_URL = 'https://myrpl.ar'

class API:

    def __init__(self, credential_manager, bearer_token=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Content-Type': 'application/json'
        }
        if bearer_token:
            self.headers['Authorization'] = f"Bearer {bearer_token}"
        self.credential_manager = credential_manager

    def login(self, username_or_email, password):
        login_url = f'{BASE_URL}/api/auth/login'
        payload = {"username_or_email": username_or_email, "password": password}
        response = requests.post(login_url, headers=self.headers, data=json.dumps(payload))
        response.raise_for_status()

        login_data = response.json()
        if 'access_token' in login_data:
            self.headers['Authorization'] = f"{login_data['token_type']} {login_data['access_token']}"
            return login_data
        else:
            raise Exception("Login failed: No access token in response")

    def fetch_courses(self):
        return self.auth_api_call('get', f'{BASE_URL}/api/courses')

    def fetch_activities(self, course_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/courses/{course_id}/activities')

    def fetch_activity_info(self, course_id, activity_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}')

    def fetch_initial_code(self, file_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/getFileForStudent/{file_id}')

    def fetch_submissions(self, course_id, activity_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/submissions')

    def fetch_final_submission(self, course_id, activity_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/finalSubmission')

    def fetch_submission_result(self, submission_id):
        return self.auth_api_call('get', f'{BASE_URL}/api/submissions/{submission_id}/result')

    def submit(self, course_id, activity_id, submission_file, description=""):
        mime_type, _ = mimetypes.guess_type(submission_file)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(submission_file, 'rb') as f:
            form = MultipartEncoder(fields={'file': (submission_file, f, mime_type), 'description': description})

        headers = self.headers.copy()
        headers['Content-Type'] = form.content_type

        return self.auth_api_call('post', f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/submissions', data=form, headers=headers)

    def auth_api_call(self, method, url, **kwargs):
        try:
            response = self.make_request(method, url, **kwargs)
            return response.json()
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                self.renew_token()
                response = self.make_request(method, url, **kwargs)
                return response.json()
            else:
                raise e

    def make_request(self, method, url, **kwargs):
        response = requests.request(method, url, headers=self.headers, **kwargs)
        response.raise_for_status()
        return response

    def renew_token(self):
        if self.credential_manager:
            username, password = self.credential_manager.get_stored_credentials()
            if not username or not password:
                raise Exception("Stored credentials not found for token renewal")
            login_result = self.login(username, password)
            self.credential_manager.store_token(login_result['access_token'])
        else:
            raise Exception("Credential manager not provided")
