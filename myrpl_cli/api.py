import json
import requests
import mimetypes
from requests_toolbelt.multipart.encoder import MultipartEncoder

BASE_URL = 'https://myrpl.ar'

class API:

    def __init__(self, bearer_token=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Content-Type': 'application/json'
        }
        if bearer_token:
            self.headers['Authorization'] = f"Bearer {bearer_token}"

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
        courses_url = f'{BASE_URL}/api/courses'
        response = requests.get(courses_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_activities(self, course_id):
        activities_url = f'{BASE_URL}/api/courses/{course_id}/activities'
        response = requests.get(activities_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_activity_info(self, course_id, activity_id):
        activity_url = f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}'
        response = requests.get(activity_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_initial_code(self, file_id):
        file_url = f'{BASE_URL}/api/getFileForStudent/{file_id}'
        response = requests.get(file_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_submissions(self, course_id, activity_id):
        submissions_url = f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/submissions'
        response = requests.get(submissions_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_final_submission(self, course_id, activity_id):
        final_submission_url = f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/finalSubmission'
        response = requests.get(final_submission_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def fetch_submission_result(self, submission_id):
        result_url = f'{BASE_URL}/api/submissions/{submission_id}/result'
        response = requests.get(result_url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def submit(self, course_id, activity_id, submission_file, description=""):
        submit_url = f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}/submissions'

        mime_type, _ = mimetypes.guess_type(submission_file)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(submission_file, 'rb') as f:
            form = MultipartEncoder(fields={'file': (submission_file, f, mime_type), 'description': description})

        headers = self.headers.copy()
        headers['Content-Type'] = form.content_type

        response = requests.post(submit_url, headers=headers, data=form)
        response.raise_for_status()
        return response.json()
