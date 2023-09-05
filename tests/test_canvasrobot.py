import mock
import builtins
import pytest

"""
1. note that this is real 
   live testing
2. please adjust the 4 constants below, 
3. at first instance of CanvasRobot you have to supply
   the URL of your Canvas environment, your Canvas API key and 
   the admin_id. 
   Both will be recorded in a secure location using the 
   [keyring](https://pypi.org/project/keyring/) library.
   Use -s as additional argument to allow user input in pytest.
   You can remove it later, after you have given the data.
"""


ADMIN_ID = 6  # If no admin_id available: set to 0
A_TEACHER_ID = 8  # choose a teacher/teacher_id from Canvas
NR_COURSES_TEACHER = 4  # lookup number of courses for this teacher
NR_COURSES_ADMIN = 130  # lookup using canvas website
TEST_COURSE = 34  # first create this test course in Canvas
TEST_COURSE_NR_ASSIGNMENTS = 8  # check if there are this number of assignments
TEST_COURSE_NR_EXAMINATIONS = 3  # make sure there are this many files in folder Tentamens

# - with assigments and at least one graded submission with file upload
# - and at least one file in folder 'Tentamens' in Files


def tst_init(cr):
    """ something with capture"""
    inputs = iter(['https://tilburguniversity.instructure.com', 'a key', 8])
    with mock.patch.object(builtins, 'input', lambda _: next(inputs)):
        assert cr


def test_getcourses_current_teacher(cr):
    """ for current teacher get the courses"""
    courses = cr.get_courses("teacher")
    assert len(list(courses)) == NR_COURSES_TEACHER


def test_getcourses_admin(cr):
    """ for the admin accpunt (if available) get the courses"""
    if ADMIN_ID:
        courses = cr.get_courses_in_account()
        assert len(list(courses)) == NR_COURSES_ADMIN


def test_api_valid(cr):
    """you need -s parameter in pytest once to record API key in keyring"""

    user = cr.get_user(8)
    assert user.id == 8


def test_course_metadata(cr):
    """ test if course_metadata collects the right data from the test course"""
    ignore_examination_names = ["Opdracht 1", ]
    md = cr.course_metadata(TEST_COURSE, ignore_examination_names)
    assert md.assignments_summary, "field assigments_summary not there"
    assert f"graded {TEST_COURSE_NR_ASSIGNMENTS}" in md.assignments_summary, \
        "assignments not reported in assigments summary"
    assert md.examination_records, "field examination_record not there"
    assert f"Total: {TEST_COURSE_NR_EXAMINATIONS}" in md.examinations_summary, \
        "examination files not (complete) in summary"


@pytest.mark.parametrize("course_id,nr_assignments,nr_examination_files",
                         [(TEST_COURSE, TEST_COURSE_NR_ASSIGNMENTS,TEST_COURSE_NR_EXAMINATIONS),
                          (12519,0,0)])

def test_update_database_from_canvas(cr,
                                     course_id,
                                     nr_assignments,
                                     nr_examination_files):
    """ To check the proces 'create and update course data':
     first delete the test course from local database if its there,
     then update testcourse (which should add it again)
     check if it's back containing the expected data."""
    cr.delete_course_from_database(course_id)
    cr.update_database_from_canvas(single_course=course_id)

    course = cr.get_course_from_database(course_id)
    assert course.course_id == course_id, "course not found, not added"
    assert course.assignments_summary, "field assigments_summary not there"
    assert f"graded {nr_assignments}" if nr_assignments \
        else "No assignments" in course.assignments_summary, \
        "no of assignments not correctly reported in assigments summary"
    # assert course.examination_candidates, "field examionation_candidates not there"
    assert f"Total: {nr_examination_files}" if nr_examination_files \
        else "No examination files" in course.examinations_summary, \
        "# of examination files not correct in summary"



def test_update_record_db(cr):
    """ Check the database updates """
    cr.update_database_from_canvas(single_course=TEST_COURSE)

    db = cr.db
    qry = (db.course.course_id == TEST_COURSE)
    cr.update_record_db(qry, "examinations_ok", True)
    course = cr.get_course_from_database(TEST_COURSE)
    assert course, f"Course {TEST_COURSE} not found"
    assert course.examinations_ok is True
    cr.update_record_db(qry, "examinations_ok", False)
    course = cr.get_course_from_database(TEST_COURSE)
    assert course.examinations_ok is False