import os
import logging
import getpass

import toml
from tqdm import tqdm

from myrpl_cli.errors import AuthError
from myrpl_cli.models import Activity
from myrpl_cli.api import API
from myrpl_cli.credential_manager import CredentialManager

logger = logging.getLogger(__name__)


class MyRPL:
    """Encapsulates general logic"""

    def __init__(self, api: API, cred_mgr: CredentialManager):
        self.api = api
        self.cred_mgr = cred_mgr
        self.api_token = None

    def login(self):
        """Asks user for credentials, stores them and saves the token"""

        username = input("Enter your username or email: ")
        password = getpass.getpass("Enter your password: ")

        try:
            login_result = self.api.login(username, password)
            self.cred_mgr.store_credentials(username, password)
            self.cred_mgr.store_token(login_result['access_token'])
            logger.info("Login successful. Credentials stored securely.")
        except AuthError as e:
            logger.error("Login failed: %s", e)

        return username, password

    def fetch_course(self, course_id, token=None, force=False):
        """Fetches all activities for a course id and saves them"""

        if token:
            self.api_token = token

        logger.info("Fetching course information for ID %i...", course_id)
        courses = self.api.fetch_courses()
        course = next(
            (course for course in courses if course.id == course_id), None)
        if course is None:
            raise ValueError(f"Course with ID {course_id} not found.")

        logger.info("Fetching activities for course: %s...", course.name)
        activities = self.api.fetch_activities(course)

        logger.info(
            "Found %i activities. Starting %s...",
            len(activities),
            'download' if force else 'update'
        )
        with tqdm(total=len(activities), unit="activity") as pbar:
            for activity in activities:
                self.save_activity(activity, pbar, force)

        logger.info(
            "All activities for course %s (ID=%i) have been successfully %s.",
            course.name,
            course.id,
            'saved' if force else 'updated'
        )

    def save_activity(self, activity: Activity, pbar, force=False):
        """
        Saves all relevant files for a given activity
        """
        
        course = activity.course

        activity = self.api.fetch_activity_info(activity)

        # Course
        course_name = course.name

        # Category
        category_name = activity.category_name
        category_description = activity.category_description

        # Activity
        activity_name = activity.name
        description = activity.description

        #   Tests
        unit_tests = activity.activity_unit_tests

        #   Initial code / last submission
        # language = activity_info.language
        initial_code = self.api.fetch_initial_code(activity)
        submission_filenames = [
            key for key in initial_code if key.endswith('.py')]
        submission_files = {}
        for filename in submission_filenames:
            submission_files[filename] = initial_code.get(filename, '')

        base_path = f'./courses/{course_name}/{category_name}/{activity_name}'
        os.makedirs(base_path, exist_ok=True)

        category_description_path = f'./courses/{course_name}/{category_name}/description.txt'
        if force or not os.path.exists(category_description_path):
            with open(category_description_path, 'w', encoding='utf8') as category_file:
                category_file.write(category_description)

        files_to_save = {
            '.myrpl': self.activity_metadata(activity),
            'description.md': description,
            **submission_files,
            'unit_test.py': unit_tests
        }

        for filename, content in files_to_save.items():
            file_path = os.path.join(base_path, filename)
            if force or not os.path.exists(file_path):
                with open(file_path, 'w', encoding='utf8') as file:
                    file.write(content)

        pbar.update(1)
        pbar.set_description(f"Saved: {activity_name}")

    def activity_metadata(self, activity: Activity) -> str:
        """Returns metadata string for a given activity"""

        return toml.dumps({
            'myrpl': {
                'course': {
                    'id': activity.course.id,
                    'name': activity.course.name,
                },
                'category': {
                    'id': activity.category.id,
                    'name': activity.category.name,
                    'description': activity.category.description
                },
                'activity': {
                    'id': activity.id,
                    'name': activity.name,
                    'description': activity.description
                }
            }
        })
