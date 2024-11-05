import mock
import builtins
import pytest
import webview
from canvasrobot.canvasrobot import Course2Foldername

"""
1. note that this is real live testing when interfacing with Canvas
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
NR_COURSES_TEACHER = 8  # lookup number of courses for this teacher
NR_COURSES_ADMIN = 178  # lookup using canvas website
TEST_COURSE = 34  # first create this test course in Canvas
TEST_COURSE_NR_ASSIGNMENTS = 8  # check if there are this number of assignments
TEST_COURSE_NR_EXAMINATIONS = 3  # make sure there are this many files in folder Tentamens

# - with assignments and at least one graded submission with file upload
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
    """ for the admin account (if available) get the courses"""
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
    assert md.assignments_summary, "field assignments_summary not there"
    assert f"graded {TEST_COURSE_NR_ASSIGNMENTS}" in md.assignments_summary, \
        "assignments not reported in assignments summary"
    assert md.examination_records, "field examination_record not there"
    assert f"Total: {TEST_COURSE_NR_EXAMINATIONS}" in md.examinations_summary, \
        "examination files not (complete) in summary"


@pytest.mark.parametrize("course_id,nr_assignments,nr_examination_files",
                         [(TEST_COURSE, TEST_COURSE_NR_ASSIGNMENTS, TEST_COURSE_NR_EXAMINATIONS),
                          (12519, 0, 0)])
def test_update_database_from_canvas(cr,
                                     course_id,
                                     nr_assignments,
                                     nr_examination_files):
    """ To check the proces 'create and update course data':
     first delete the test course from local database if its there,
     then run update course from Canvas source (which should add it again)
     check if it's back and containing the expected data."""
    result = cr.delete_course_from_database(course_id)
    print(f"{result} records (recursive) deleted")
    if result == 0:
        print("Note: update database from canvas could not not be tested")

        return True  # I know, but we cannot update if it's missing!
    cr.update_database_from_canvas(single_course=course_id)

    course = cr.get_course_from_database(course_id)
    assert course.course_id == course_id, "course not found, not added"
    assert course.assignments_summary, "field assignments_summary not there"
    assert f"graded {nr_assignments}" if nr_assignments \
        else "No assignments" in course.assignments_summary, \
        "no of assignments not correctly reported in assignments summary"
    # assert course.examination_candidates, "field examination_candidates not there"
    assert f"Total: {nr_examination_files}" if nr_examination_files \
        else "No examination files" in course.examinations_summary, \
        "# of examination files not correct in summary"


def test_update_record_db(cr):
    """ Check the database after updating single record"""
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


def test_outliner_foldernames(cr):
    cr.outliner_foldernames.append(Course2Foldername(34, "Tentamens"))
    cr.outliner_foldernames.append(Course2Foldername(35, "Tentamens 3"))

    output = cr.print_outliner_foldernames()

    assert "34" in output, f"error in printing foldernames: {output}"
    assert "35" in output, f"error in printing foldernames: {output}"
    assert "Tentamens" in output, f"error in printing foldernames: {output}"
    assert "Tentamens 3" in output, f"error in printing foldernames: {output}"


def test_search_replace(cr):
    """check if course_search_replace function works"""
    db = cr.db
    course = cr.get_course(TEST_COURSE)
    pages = course.get_pages(include=['body'])
    search_text, replace_text = ' je', ' u'
    page_found_url = ""
    dryrun = True
    for page in pages:
        if search_text in page.body:
            page_found_url = page.url  # remember
            cr.search_replace_in_page(page, search_text, replace_text, dryrun=dryrun)
            # We only need one page to test this
            break

    if page_found_url:
        if not dryrun:
            # read again from canvas instance to check
            page = course.get_page(page_found_url)
            assert search_text not in page.body
            assert replace_text in page.body
    else:
        assert False, f"Source string '{search_text}' not found in any page of course {TEST_COURSE}"
