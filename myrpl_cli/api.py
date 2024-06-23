from typing import List
import mimetypes
import json

import requests
from requests_toolbelt.multipart.encoder import MultipartEncoder

from myrpl_cli.errors import MissingCredentialsError
from myrpl_cli.models import Course, Activity, Submission, SubmissionResult
from myrpl_cli.credential_manager import CredentialManager

BASE_URL = 'https://myrpl.ar'


class API:
    """API client for myrpl.ar"""

    def __init__(self, credential_manager: CredentialManager, bearer_token=None):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Content-Type': 'application/json'
        }
        if bearer_token:
            self.headers['Authorization'] = f"Bearer {bearer_token}"
        self.credential_manager = credential_manager

    def login(self, username_or_email, password):
        """Obtains a bearer token given email & password"""

        login_url = f'{BASE_URL}/api/auth/login'
        payload = {
            "username_or_email": username_or_email,
            "password": password
        }
        response = requests.post(
            login_url,
            headers=self.headers,
            data=json.dumps(payload),
            timeout=10
        )
        response.raise_for_status()

        login_data = response.json()

        self.headers['Authorization'] = f"{login_data['token_type']} {login_data['access_token']}"
        return login_data

    def fetch_courses(self) -> List[Course]:
        """Fetches all courses"""

        courses_response = self.auth_api_call('get', f'{BASE_URL}/api/courses')
        courses = [
            Course(**course)
            for course in courses_response
        ]
        return courses

    def fetch_activities(self, course: Course) -> List[Activity]:
        """Fetches all activities in a course"""

        activities_response = self.auth_api_call(
            'get',
            f'{BASE_URL}/api/courses/{course.id}/activities'
        )
        activities = [
            Activity(course=course, **activity)
            for activity in activities_response
        ]
        return activities

    def fetch_activity_info(self, activity: Activity) -> Activity:
        """Fetches all info on an activity"""

        activity_info_response = self.auth_api_call(
            'get',
            f'{BASE_URL}/api/courses/{activity.course.id}/activities/{activity.id}'
        )

        return Activity(
            course=activity.course,
            **activity_info_response
        )

    def fetch_initial_code(self, activity: Activity):
        """Fetches the initial code snippet for a given activity"""

        return self.auth_api_call(
            'get',
            f'{BASE_URL}/api/getFileForStudent/{activity.file_id}'
        )

    def fetch_submissions(self, activity: Activity):
        """Fetches all submissions for a given activity"""

        submissions_response = self.auth_api_call(
            'get',
            f'{BASE_URL}/api/courses/{activity.course.id}/activities/{activity.id}/submissions'
        )
        submissions = [
            Submission(activity=activity, **submission)
            for submission in submissions_response
        ]
        return submissions

    def fetch_final_submission(self, activity: Activity):
        """Fetches the final (definitive) submission for a given activity"""

        final_submission_response = self.auth_api_call(
            'get',
            f'{BASE_URL}/api/courses/{activity.course.id}/activities/{activity.id}/finalSubmission'
        )
        return Submission(
            activity=activity,
            **final_submission_response,
            is_final_solution=True
        )

    def fetch_submission_result(self, submission: Submission) -> SubmissionResult:
        """Fetches the result of a given submission"""

        submission_result_response = self.auth_api_call(
            'get',
            f'{BASE_URL}/api/submissions/{submission.id}/result'
        )
        return SubmissionResult(
            submission=submission,
            activity=submission.activity,
            **submission_result_response
        )

    def submit(self, activity: Activity, submission_file: str, description: str = ""):
        """Submits a submission for an activity"""

        mime_type, _ = mimetypes.guess_type(submission_file)
        if mime_type is None:
            mime_type = 'application/octet-stream'

        with open(submission_file, 'rb') as f:
            form = MultipartEncoder(
                fields={
                    'file': (submission_file, f, mime_type),
                    'description': description
                }
            )

        headers = self.headers.copy()
        headers['Content-Type'] = form.content_type

        return self.auth_api_call(
            'post',
            f'{BASE_URL}/api/courses/{activity.course.id}/activities/{activity.id}/submissions',
            data=form,
            headers=headers
        )

    def auth_api_call(self, method: str, url: str, **kwargs) -> dict:
        """Makes a generic authed API call"""

        if self.headers.get('Authorization', None) is None:
            self.headers['Authorization'] = f"Bearer {self.credential_manager.get_stored_token()}"

        headers = {
            **self.headers,
            **(kwargs.get('headers', {}))
        }

        try:
            response = self.make_request(
                method,
                url,
                **kwargs,
                headers=headers
            )
        except requests.HTTPError as e:
            if e.response.status_code == 401:
                self.renew_token()
                response = self.make_request(
                    method,
                    url,
                    **kwargs,
                    headers=headers
                )
            else:
                raise e

        return response.json()

    def make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Makes a generic API call"""

        response = requests.request(
            method,
            url,
            **kwargs,
            timeout=10
        )
        response.raise_for_status()
        return response

    def renew_token(self):
        """Renews the API token using the stored credentials"""

        username, password = self.credential_manager.get_stored_credentials()
        if not username or not password:
            raise MissingCredentialsError(
                "Stored credentials not found for token renewal")

        login_result = self.login(username, password)
        self.credential_manager.store_token(login_result['access_token'])
        self.headers['Authorization'] = f"Bearer {login_result['access_token']}"
