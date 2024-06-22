import argparse
import os
from dotenv import load_dotenv
from myrpl_cli.myrpl_api import MYRPL_API
from tqdm import tqdm

load_dotenv()

def save_activity(api, course, activity, pbar):
    course_id = course['id']
    course_name = course['name']
    activity_id = activity['id']

    activity_info = api.fetch_activity_info(course_id, activity_id)

    category_name = activity_info['category_name']
    activity_name = activity_info['name']
    category_description = activity_info['category_description']
    description = activity_info['description']
    language = activity_info['language']
    unit_tests = activity_info['activity_unit_tests']
    file_id = activity_info['file_id']

    initial_code = api.fetch_initial_code(file_id)
    main_py_content = initial_code.get('main.py', '')

    base_path = f'./courses/{course_name}/{category_name}/{activity_name}'
    os.makedirs(base_path, exist_ok=True)

    category_description_path = f'./courses/{course_name}/{category_name}/description.txt'
    if not os.path.exists(category_description_path):
        with open(category_description_path, 'w') as category_file:
            category_file.write(category_description)

    with open(f'{base_path}/description.md', 'w') as description_file:
        description_file.write(description)

    with open(f'{base_path}/main.py', 'w') as activity_file:
        activity_file.write(main_py_content)

    with open(f'{base_path}/unit_test.py', 'w') as unit_test_file:
        unit_test_file.write(unit_tests)

    pbar.update(1)
    pbar.set_description(f"Saved: {activity_name}")

def fetch_course(api, course_id):
    print(f"Fetching course information for ID {course_id}...")
    courses = api.fetch_courses()
    course = next((course for course in courses if course['id'] == course_id), None)
    if course is None:
        raise ValueError(f"Course with ID {course_id} not found.")

    print(f"Fetching activities for course: {course['name']}...")
    activities = api.fetch_activities(course_id)

    print(f"Found {len(activities)} activities. Starting download...")
    with tqdm(total=len(activities), unit="activity") as pbar:
        for activity in activities:
            save_activity(api, course, activity, pbar)

    print(f"All activities for course ID {course_id} have been successfully saved.")

def main():
    parser = argparse.ArgumentParser(description="CLI tool for MyRPL course activities")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Fetch command
    fetch_parser = subparsers.add_parser("fetch", help="Fetch and save activities for a given course ID")
    fetch_parser.add_argument("course_id", type=int, help="ID of the course to fetch activities from")
    fetch_parser.add_argument("-t", "--token", help="Bearer token for authentication. If not provided, uses MYRPL_BEARER_TOKEN from environment")

    args = parser.parse_args()

    if args.command == "fetch":
        bearer_token = args.token if args.token else os.getenv('MYRPL_BEARER_TOKEN')
        if not bearer_token:
            parser.error("Bearer token must be provided either via --token argument or MYRPL_BEARER_TOKEN environment variable")

        print("Initializing API connection...")
        api = MYRPL_API(bearer_token)
        fetch_course(api, args.course_id)
    elif args.command is None:
        parser.print_help()

if __name__ == "__main__":
    main()
