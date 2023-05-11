from typing import List
from datetime import datetime
from attrs import define
# from dataclasses import dataclass, field


@define
class Course:
    course_id: int = 0
    name: str = ""
    course_code: str = ""
    sis_code: str = ""
    creation_date: datetime = None
    ac_year: int = 1961
    teachers: List[str] = []
    teacher_names: List[str] = []


@define
class EnrollDTO:
    username: str
    course: str
    role: str
    user_id: int = 0
    course_id: int = 0

@define
class SearchTextInCourseDTO:
    course_id: int = 0
    course: str = ""
    search: str = ""

@define
class ExaminationDTO:
    course_id: int
    course_name: str
    name:str

@define
class CourseMetadata:
    nr_modules: int
    nr_module_items: int
    nr_pages: int
    nr_assignments: int
    nr_quizzes: int
    nr_files: int
    assignments_summary: str
    examinations_summary: str
    examination_records: list[ExaminationDTO]
    # nr_collaborations: int

    # #ext_urls: int
    # avr_len_assignments: int

@define
class Grade:
    stud_name: str
    stud_id: str
    final_score: float
    final_grade: float

