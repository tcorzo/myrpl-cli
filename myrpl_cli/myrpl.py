import os
import logging
import getpass
from typing import Optional

import pytest
import toml
from tqdm import tqdm

from myrpl_cli.errors import AuthError, NotMyRPLDirectoryError
from myrpl_cli.models import Activity, MyRPLMetadata
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

    def test(self, pytest_args):
        """
        Run tests for current directory (course/category/activity)
        """

        meta = self.open_metadata()
        if meta is None:
            logger.error("can't run tests outside a myrpl directory")
            return

        logger.info("Running tests for:")
        if meta.course is not None:
            logger.info("Course: %s", meta.course.name)
        if meta.category is not None:
            logger.info("└──Category: %s", meta.category.name)
        if meta.activity is not None:
            logger.info("\t└──Activity: %s", meta.activity.name)

        pytest.main(pytest_args)

        logger.info("Finished tests for:")
        if meta.course is not None:
            logger.info("Course: %s", meta.course.name)
        if meta.category is not None:
            logger.info("└──Category: %s", meta.category.name)
        if meta.activity is not None:
            logger.info("\t└──Activity: %s", meta.activity.name)

    def open_metadata(self) -> Optional[MyRPLMetadata]:
        """
        Reads, parses and returns the current directory's metadata
        """

        if not os.path.exists('.myrpl'):
            raise NotMyRPLDirectoryError()

        return MyRPLMetadata(**toml.load('.myrpl'))

    def save_activity(self, activity: Activity, pbar, force=False):
        """
        Saves all relevant files for a given activity
        """

        course = activity.course
        category = activity.category
        course_path = f'./courses/{course.name}'
        category_path = f'./courses/{course.name}/{category.name}'
        activity_path = f'./courses/{course.name}/{category.name}/{activity.name}'

        if os.path.exists(f'{activity_path}/') and not force:
            pbar.update(1)
            pbar.set_description(f"Skipped: {activity.name}, already exists")
            return

        activity = self.api.fetch_activity_info(activity)
        os.makedirs(activity_path, exist_ok=True)

        course_metadata_path = os.path.join(course_path, '.myrpl')
        if not os.path.exists(f'{course_metadata_path}/'):
            with open(course_metadata_path, 'w', encoding='utf8') as file:
                file.write(toml.dumps(course.metadata().model_dump()))

        category_metadata_path = os.path.join(category_path, '.myrpl')
        if not os.path.exists(f'{category_metadata_path}/'):
            with open(category_metadata_path, 'w', encoding='utf8') as file:
                file.write(toml.dumps(category.metadata().model_dump()))

        category_description_path = f'./courses/{course.name}/{category.name}/description.txt'
        with open(category_description_path, 'w', encoding='utf8') as category_file:
            category_file.write(category.description)

        code_files = self.get_code_files(activity)
        code_files = {
            k: v for k,
            v in code_files.items() if k.endswith('.py')
        }

        files_to_save = {
            '.myrpl': toml.dumps(activity.metadata().model_dump()),
            'description.md': activity.description,
            **code_files,
            'unit_test.py': activity.activity_unit_tests
        }

        for filename, content in files_to_save.items():
            file_path = os.path.join(activity_path, filename)
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
