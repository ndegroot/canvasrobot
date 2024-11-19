from .canvasrobot import CanvasRobot, LocalDAL, \
    EDUCATIONS, COMMUNITIES
from .canvasrobot_model import STUDADMIN, SHORTNAMES, Field
__all__ = ["CanvasRobot", "LocalDAL", "Field", "ENROLLMENT_TYPES", "EDUCATIONS", "COMMUNITIES",
            "STUDADMIN", "SHORTNAMES"]
__version__ = "0.7.3"  # It MUST match the version in pyproject.toml file