from .canvasrobot import CanvasRobot, LocalDAL, \
    EDUCATIONS, COMMUNITIES
from .canvasrobot_model import STUDADMIN, SHORTNAMES, Field
from .urltransform import UrlTransformationRobot, show_result
from .commandline import show_search_result, search_replace_show, get_logger

__all__ = ["CanvasRobot", "UrlTransformationRobot", "LocalDAL", "Field",
           "ENROLLMENT_TYPES", "EDUCATIONS", "COMMUNITIES",
           "STUDADMIN", "SHORTNAMES",
           "get_logger", "show_result", "show_search_result", "search_replace_show"]

__version__ = "0.8.4"  # It MUST match the version in pyproject.toml file
