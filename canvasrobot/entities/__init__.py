from dataclasses import dataclass
from typing import TypeVar, Generic, List, Dict, Tuple

from .course import Course, EnrollDTO, SearchTextInCourseDTO
from .user import User
from .guest import Guest
from .quiz import Answer, QuizDTO, QuestionDTO, Stats
