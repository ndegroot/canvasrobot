from typing import List
from datetime import datetime

from dataclasses import dataclass, field


@dataclass
class Course:
    course_id: int = 0
    name: str = ""
    course_code: str = ""
    sis_code: str = ""
    creation_date: datetime = None
    ac_year: int = 1961
    teachers: List[str] = field(default_factory=list)
    teacher_names: List[str] = field(default_factory=list)


@dataclass
class EnrollDTO:
    username: str
    course: str
    role: str
    user_id: int = 0
    course_id: int = 0

@dataclass
class SearchTextInCourseDTO:
    course_id: int = 0
    course: str = ""
    search: str = ""
