from canvasrobot import CanvasRobot
import mock
import builtins
from .test_base import set_keyboard_input


def tst_init():
    """ something with capture"""
    inputs = iter(['https://tilburguniversity.instructure.com', 'a key', 8])
    with mock.patch.object(builtins, 'input', lambda _: next(inputs)):
        cr = CanvasRobot()
        assert cr



"""
1. please adjust the 4 constants below, note that this is real 
   live testing
2. at first instance of CanvasRobot you have to supply
   the URL of your Canvas environment, your Canvas API key and 
   the admin_id. 
   Both will be recorded in a secure location using the 
   [keyring](https://pypi.org/project/keyring/) library.
   Use -s as additional argument to allow user input in pytest.
   You can remove it later, after you have given the data.
"""


ADMIN_ID = 6  # If no admin_id available: set to 0
A_TEACHER_ID = 8  # choose a teacher/teacher_id from Canvas
NR_COURSES_USER = 5  # lookup number of courses for this teacher
NR_COURSES_ADMIN = 125  # lookup using canvas website

cr = CanvasRobot()


def test_getcourses_current_user():
    """ for current user get the courses"""
    courses = cr.get_courses("teacher")
    assert len(list(courses)) == NR_COURSES_USER


def test_getcourses_admin():
    """ for the admin accpunt (if available) get the courses"""
    if ADMIN_ID:
        courses = cr.get_courses_in_account("teacher")
        assert len(list(courses)) == NR_COURSES_ADMIN

def test_api_valid():
    """you need -s parameter in pytest once to record API key in keyring"""

    user = cr.get_user(8)
    assert user.id==8