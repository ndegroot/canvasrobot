from .canvasrobot import CanvasRobot, LocalDAL, COMMUNITIES
from .canvasrobot_model import STUDADMIN, SHORTNAMES, ENROLLMENT_TYPES, Field
from .urltransformRobot import UrlTransformationRobot, show_result, Transformation, cli, scan_replace_urls
from .commandline import show_search_result, get_logger, create_db_folder

__all__ = ["CanvasRobot", "UrlTransformationRobot", "LocalDAL", "Field",
           "ENROLLMENT_TYPES", "EDUCATIONS", "COMMUNITIES",
           "STUDADMIN", "SHORTNAMES",
           "get_logger", "show_result", "cli", "show_search_result", "search_replace_show", "TransformedPage"]

__version__ = "0.8.4"  # It MUST match the version in pyproject.toml file
