import requests

BASE_URL = 'https://myrpl.ar'

class MYRPL_API:
    def __init__(self, bearer_token) -> None:
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
            'Authorization': f'Bearer {bearer_token}',
            'Content-Type': 'application/json'
        }

    def fetch_courses(self):
        courses_url = f'{BASE_URL}/api/courses'
        response = requests.get(courses_url, headers=self.headers)
        courses = response.json()

        return courses

    def fetch_activities(self, course_id):
        activities_url = f'{BASE_URL}/api/courses/{course_id}/activities'
        response = requests.get(activities_url, headers=self.headers)
        activities = response.json()

        return activities

    def fetch_activity_info(self, course_id, activity_id):
        activity_url = f'{BASE_URL}/api/courses/{course_id}/activities/{activity_id}'
        response = requests.get(activity_url, headers=self.headers)
        activity_info = response.json()

        return activity_info

    def fetch_initial_code(self, file_id):
        file_url = f'{BASE_URL}/api/getFileForStudent/{file_id}'
        response = requests.get(file_url, headers=self.headers)
        file_content = response.json()

        return file_content
