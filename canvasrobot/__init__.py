from .canvasrobot import CanvasRobot, LocalDAL,ENROLLMENT_TYPES, \
    EDUCATIONS, COMMUNITIES
from .canvasrobot_model import STUDADMIN, SHORTNAMES
__all__=["CanvasRobot","LocalDAL","ENROLLMENT_TYPES","EDUCATIONS","COMMUNITIES",
         "STUDADMIN","SHORTNAMES"]
__version__ = "0.7.1" # It MUST match the version in pyproject.toml file