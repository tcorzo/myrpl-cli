from typing import List, Optional, Literal

from pydantic import (
    BaseModel,
    computed_field,
    field_validator
)


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

    category_id: int
    category_name: str
    category_description: str

    @computed_field
    def category(self) -> Category:
        return Category(
            course=self.course,
            id=self.category_id,
            name=self.category_name,
            description=self.category_description,
        )

    id: int
    name: str
    description: str

    language: str
    activity_unit_tests: Optional[str] = None
    file_id: int
    submission_status: Optional[Literal["SUCCESS", "FAILURE"]] = None

    @field_validator('submission_status', mode='before')
    @classmethod
    def empty_str_to_none(cls, v: str) -> Optional[str]:
        """Coerses empty string to None"""
        if v == "":
            return None
        return v


class UnitTestResult(BaseModel):
    """UnitTestResult model"""

    id: int
    test_name: str
    passed: bool
    error_messages: Optional[str] = None


class Submission(BaseModel):
    """Submission model"""

    @field_validator('submission_status', mode='before')
    @classmethod
    def empty_str_to_none(cls, v: str) -> Optional[str]:
        """Coerses empty string to None"""
        if v == "":
            return None
        return v

    id: int
    activity: Activity
    submission_file_name: str
    submission_file_type: str
    submission_file_id: int
    is_iotested: bool
    activity_starting_files_name: str
    activity_starting_files_type: str
    activity_starting_files_id: int
    activity_language: str
    activity_unit_tests: Optional[str] = None
    submission_status: Optional[Literal["SUCCESS", "FAILURE"]] = None
    is_final_solution: Optional[bool] = None
    exit_message: Optional[str] = None
    stderr: Optional[str] = None
    stdout: Optional[str] = None
    io_test_run_results: List[dict] = []
    unit_test_run_results: List[UnitTestResult] = []
    submission_date: Optional[str] = None


class SubmissionResult(Submission):
    """SubmissionResult model"""

    submission: Submission


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
