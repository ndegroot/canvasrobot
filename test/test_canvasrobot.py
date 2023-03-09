from canvasrobot import CanvasRobot
import mock
import builtins


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
NR_COURSES_ADMIN = 129  # lookup using canvas website
TEST_COURSE = 34 # first create a test course in Canvas
TEST_COURSE_NR_ASSIGNMENTS = 8
TEST_COURSE_NR_EXAMINATIONS = 4 # first create a test course in Canvas

# - with assigments and at least one graded submission with file upload
# - and at least one file in folder 'Tentamens' in Files

cr = CanvasRobot()


def test_getcourses_current_user():
    """ for current user get the courses"""
    courses = cr.get_courses("teacher")
    assert len(list(courses)) == NR_COURSES_USER


def tst_getcourses_admin():
    """ for the admin accpunt (if available) get the courses"""
    if ADMIN_ID:
        courses = cr.get_courses_in_account()
        assert len(list(courses)) == NR_COURSES_ADMIN

def test_api_valid():
    """you need -s parameter in pytest once to record API key in keyring"""

    user = cr.get_user(8)
    assert user.id==8

def test_course_metadata():
    """ test if course_metadata collects the rigth data from the test course"""
    canonical_examination_names = ["deeltentamen",]
    md = cr.course_metadata(TEST_COURSE, canonical_examination_names)
    assert md.assignments_summary, "field assigments_summary not there"
    assert f"graded {TEST_COURSE_NR_ASSIGNMENTS}" in md.assignments_summary, \
        "assignments not reported in assigments summary"
    assert md.examination_candidates, "field examination_candidates not there"
    assert f"Total: {TEST_COURSE_NR_EXAMINATIONS}" in md.examinations_summary, \
        "examination files not (complete) in summary"

def test_update_database_from_canvas():
    """ delete the test couirse from local database,
     update (which should add it agian)
     check if it's back """
    cr.delete_course_from_database(TEST_COURSE)
    cr.update_database_from_canvas(single_course=TEST_COURSE)
    course = cr.get_course_from_database(TEST_COURSE)
    assert course.course_id==TEST_COURSE, "course not added"
    assert course.assignments_summary, "field assigments_summary not there"
    assert f"graded {TEST_COURSE_NR_ASSIGNMENTS}" in course.assignments_summary, \
        "assignments not reported in assigments summary"
    #assert course.examination_candidates, "field examionation_candidates not there"
    assert f"Total: {TEST_COURSE_NR_EXAMINATIONS}" in course.examinations_summary, \
        "examination files not (complete) in summary"

def test_update_record_db():
    cr.update_record_db( "course_id", TEST_COURSE, "course", "examinations_ok", True)
    course = cr.get_course_from_database(TEST_COURSE)
    assert course.examinations_ok is True
    cr.update_record_db( "course_id", TEST_COURSE, "course", "examinations_ok", False)
    course = cr.get_course_from_database(TEST_COURSE)
    assert course.examinations_ok is False
