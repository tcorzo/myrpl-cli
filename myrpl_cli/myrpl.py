import os
from tqdm import tqdm
import logging
import getpass

from myrpl_cli.api import API
from myrpl_cli.credential_manager import CredentialManager

logger = logging.getLogger(__name__)

class MyRPL:

    def __init__(self, api: API, cred_mgr: CredentialManager):
        self.api = api
        self.cred_mgr = cred_mgr
        self.api_token = None

    def login(self):
        username = input("Enter your username or email: ")
        password = getpass.getpass("Enter your password: ")

        try:
            login_result = self.api.login(username, password)
            self.cred_mgr.store_credentials(username, password)
            self.cred_mgr.store_token(login_result['access_token'])
            logger.info("Login successful. Credentials stored securely.")
        except Exception as e:
            logger.error(f"Login failed: {e}")

        return username, password

    def fetch_course(self, course_id, token=None, force=False):
        if token:
            self.api_token = token

        logger.info(f"Fetching course information for ID {course_id}...")
        courses = self.api.fetch_courses()
        course = next((course for course in courses if course['id'] == course_id), None)
        if course is None:
            raise ValueError(f"Course with ID {course_id} not found.")

        logger.info(f"Fetching activities for course: {course['name']}...")
        activities = self.api.fetch_activities(course_id)

        logger.info(f"Found {len(activities)} activities. Starting {'download' if force else 'update'}...")
        with tqdm(total=len(activities), unit="activity") as pbar:
            for activity in activities:
                self.save_activity(course, activity, pbar, force)

        logger.info(f"All activities for course {course['name']} (ID={course_id}) have been successfully {'saved' if force else 'updated'}.")

    def save_activity(self, course, activity, pbar, force=False):
        course_id = course['id']
        course_name = course['name']
        activity_id = activity['id']

        activity_info = self.api.fetch_activity_info(course_id, activity_id)

        category_name = activity_info['category_name']
        activity_name = activity_info['name']
        category_description = activity_info['category_description']
        description = activity_info['description']
        language = activity_info['language'] # TODO provide per language support
        unit_tests = activity_info['activity_unit_tests']
        file_id = activity_info['file_id']

        initial_code = self.api.fetch_initial_code(file_id)
        submission_filenames = [key for key in initial_code if key.endswith('.py')]
        submission_files = {}
        for filename in submission_filenames:
            submission_files[filename] = initial_code.get(filename, '')

        base_path = f'./courses/{course_name}/{category_name}/{activity_name}'
        os.makedirs(base_path, exist_ok=True)

        category_description_path = f'./courses/{course_name}/{category_name}/description.txt'
        if force or not os.path.exists(category_description_path):
            with open(category_description_path, 'w') as category_file:
                category_file.write(category_description)

        files_to_save = {
            'description.md': description,
            'unit_test.py': unit_tests,
            **submission_files
        }

        for filename, content in files_to_save.items():
            file_path = os.path.join(base_path, filename)
            if force or not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write(content)

        pbar.update(1)
        pbar.set_description(f"Saved: {activity_name}")
