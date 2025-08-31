import os
from canvasrobot import CanvasRobot, show_search_result, search_replace_show
from canvasrobot.commandline import enroll_student, search_replace_pages
TEST_COURSE = 34  # first create this test course in Canvas


def run():
    robot = CanvasRobot(reset_api_keys=False,
                        db_force_update=False)

    # robot.update_database_from_canvas()
    # result = robot.get_students_dibsa('PM_MACS', local=False)
    # result = robot.search_user('u144466', 'A.J.D.Hendriks@tilburguniversity.edu')
    # result2 = robot.enroll_in_course(search="", course_id=4230, username='u144466')
    # above needs ncdg sis_str version canvasapi
    # robot.get_courses_in_account()

    # enroll_student(robot)  # working!
    # courses = robot.get_courses_in_account()
    # search_replace_pages(robot)

    course = robot.get_course(TEST_COURSE)
    robot.update_db_for(course)
    # rows = robot.get_list_of_documents_db(course_id=TEST_COURSE)
    robot.report_errors()


if __name__ == '__main__':
    # # path = os.path.dirname(__file__)
    # import webview
    # win = webview.create_window("pad", "index.html",
    #                             # title="Preview (click button to close)",
    #                             # html=html,
    #                             # js_api=api
    #                             )
    # #api.set_window(win)
    # webview.start(debug=True)

    run()
