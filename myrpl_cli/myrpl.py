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
            (course
             for course in courses if course.id == course_id),
            None
        )
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
        category = activity.category
        base_path = f'./courses/{course.name}/{category.name}/{activity.name}'

        if os.path.exists(f'{base_path}/') and not force:
            pbar.update(1)
            pbar.set_description(f"Skipped: {activity.name}, already exists")
            return

        activity = self.api.fetch_activity_info(activity)

        code_files = self.get_code_files(activity)
        code_files = {
            k: v for k,
            v in code_files.items() if k.endswith('.py')
        }

        os.makedirs(base_path, exist_ok=True)

        category_description_path = f'./courses/{course.name}/{category.name}/description.txt'
        with open(category_description_path, 'w', encoding='utf8') as category_file:
            category_file.write(category.description)

        files_to_save = {
            '.myrpl': self.activity_metadata(activity),
            'description.md': activity.description,
            **code_files,
            'unit_test.py': activity.activity_unit_tests
        }

        for filename, content in files_to_save.items():
            file_path = os.path.join(base_path, filename)
            with open(file_path, 'w', encoding='utf8') as file:
                file.write(content)

        pbar.update(1)
        pbar.set_description(f"Saved: {activity.name}")

    def get_code_files(self, activity):
        """
        Gets the latest submission or the initial code snippet files
        """
        if activity.submission_status is not None:
            submissions = self.api.fetch_submissions(activity)
            submissions.sort(key=lambda s: s.id)

            last_submission = submissions[-1]
            return self.api.fetch_files(
                last_submission.submission_file_id
            )
        else:
            return self.api.fetch_files(activity.file_id)

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
