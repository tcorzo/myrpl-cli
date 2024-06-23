from typing import List, Optional

from pydantic import BaseModel


class Course(BaseModel):
    """Course model"""
    id: int
    name: str


class Category(BaseModel):
    """Category model"""
    course: Course

    id: int
    name: str
    description: str


class Activity(BaseModel):
    """Activity model"""
    course: Course
    category: Category

    id: int
    name: str
    category_name: str
    name: str
    category_description: str
    description: str
    language: str
    activity_unit_tests: str
    file_id: int


class SubmissionResult(BaseModel):
    """SubmissionResult model"""

    # Define fields as per your API response structure
    pass


class UnitTestResult(BaseModel):
    """UnitTestResult model"""

    id: int
    test_name: str
    passed: bool
    error_messages: Optional[str]


class Submission(BaseModel):
    """Submission model"""

    id: int
    activity_id: int
    submission_file_name: str
    submission_file_type: str
    submission_file_id: int
    is_iotested: bool
    activity_starting_files_name: str
    activity_starting_files_type: str
    activity_starting_files_id: int
    activity_language: str
    activity_unit_tests: str
    submission_status: str
    is_final_solution: bool
    exit_message: str
    stderr: str
    stdout: str
    io_test_run_results: List[dict]  # Define structure based on actual data
    unit_test_run_results: List[UnitTestResult]
    submission_date: str


class CourseMetadata(BaseModel):
    """CourseMetadata model"""

    id: int
    name: str


class CategoryMetadata(BaseModel):
    """CategoryMetadata model"""

    course: CourseMetadata
    id: int
    name: str


class ActivityMetadata(BaseModel):
    """ActivityMetadata model"""

    course: CourseMetadata
    category: CategoryMetadata
    id: int
    name: str
    description: str
