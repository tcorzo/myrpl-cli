# myrpl.py

import os
from tqdm import tqdm

import getpass

from myrpl_cli.api import API
from myrpl_cli.credential_manager import CredentialManager

class MyRPL:

    def __init__(self):
        self.api = API()
        self.cred_mgr = CredentialManager()
        self.api_token = None

    def login(self) -> tuple[str, str]:
        username = input("Enter your username or email: ")
        password = getpass.getpass("Enter your password: ")

        try:
            login_result = self.api.login(username, password)
            self.cred_mgr.store_credentials(username, password)
            self.cred_mgr.store_token(login_result['access_token'])
            print("Login successful. Credentials stored securely.")
        except Exception as e:
            print(f"Login failed: {e}")

        return username, password

    def fetch_course(self, api, course_id, token, force=False):
        if token:
            self.api_token = token

        print(f"Fetching course information for ID {course_id}...")
        courses = api.fetch_courses()
        course = next((course for course in courses if course['id'] == course_id), None)
        if course is None:
            raise ValueError(f"Course with ID {course_id} not found.")

        print(f"Fetching activities for course: {course['name']}...")
        activities = api.fetch_activities(course_id)

        print(f"Found {len(activities)} activities. Starting {'download' if force else 'update'}...")
        with tqdm(total=len(activities), unit="activity") as pbar:
            for activity in activities:
                self.save_activity(api, course, activity, pbar, force)

        print(f"All activities for course {course['name']} (ID={course_id}) have been successfully {'saved' if force else 'updated'}.")

    def save_activity(self, api, course, activity, pbar, force=False):
        course_id = course['id']
        course_name = course['name']
        activity_id = activity['id']

        activity_info = api.fetch_activity_info(course_id, activity_id)

        category_name = activity_info['category_name']
        activity_name = activity_info['name']
        category_description = activity_info['category_description']
        description = activity_info['description']
        language = activity_info['language'] # TODO provide per language support
        unit_tests = activity_info['activity_unit_tests']
        file_id = activity_info['file_id']

        initial_code = api.fetch_initial_code(file_id)
        main_py_content = initial_code.get('main.py', '')

        base_path = f'./courses/{course_name}/{category_name}/{activity_name}'
        os.makedirs(base_path, exist_ok=True)

        category_description_path = f'./courses/{course_name}/{category_name}/description.txt'
        if force or not os.path.exists(category_description_path):
            with open(category_description_path, 'w') as category_file:
                category_file.write(category_description)

        files_to_save = {
            'description.md': description,
            'main.py': main_py_content,
            'unit_test.py': unit_tests
        }

        for filename, content in files_to_save.items():
            file_path = os.path.join(base_path, filename)
            if force or not os.path.exists(file_path):
                with open(file_path, 'w') as file:
                    file.write(content)

        pbar.update(1)
        pbar.set_description(f"Saved: {activity_name}")

    def auth_api_call(self):
        if self.api_token is None:
            self.api_token = self.get_api_token()
        # try request

    def get_api_token(self):
        api_token = self.api_token
        if not api_token is None:
            return api_token

        api_token = self.cred_mgr.get_stored_token()
        if not api_token is None:
            return api_token

        username, password = self.cred_mgr.get_stored_credentials()
        if not username or not password:
            username, password = self.login()

        login_result = self.api.login(username, password)
        api_token = login_result['access_token']
        if not api_token is None:
            return api_token

        raise Exception('All authentication methods failed')

    def invalidate_token(self):
        self.api_token = None
        self.cred_mgr.store_token(None)
