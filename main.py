import logging
import sys

import rich
import webview
import canvasrobot as cr

logger = logging.getLogger("canvasrobot.canvasrobot")
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
file_handler = logging.FileHandler("canvasrobot.log")
file_handler.setFormatter(formatter)
file_handler.setLevel(logging.WARNING)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
stream_handler.setLevel(logging.INFO)

logger.addHandler(file_handler)
logger.addHandler(stream_handler)

logger.info(f"{__name__} started")

TEST_COURSE = 34  # first create this test course in Canvas


def search_replace_show(cr):
    """check course_search_replace function dryrun, show"""
    # db = cr.db
    course = cr.get_course(TEST_COURSE)
    pages = course.get_pages(include=['body'])
    search_text, replace_text = ' je', ' u'
    page_found_url = ""
    dryrun = True
    for page in pages:
        if search_text in page.body:
            page_found_url = page.url  # remember
            count, html = cr.search_replace_in_page(page, search_text, replace_text, dryrun=dryrun)
            # We only need one page to test this
            if dryrun:
                show_search_result(count, html)
            break

    if page_found_url:
        if not dryrun:
            # read again from canvas instance to check
            page = course.get_page(page_found_url)
            assert search_text not in page.body
            assert replace_text in page.body
    else:
        assert False, f"Source string '{search_text}' not found in any page of course {TEST_COURSE}"


def show_search_result(count: int, html: str):

    template = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Zoekresultaat</title>
    </head>
    <body>
      <p>In <span style='color: red;' >red</span> below the {} found locations</p>
      <button onclick='pywebview.api.close()'>Klaar?</button>
      <hr/>
      {}  
    </body>
    </html>
    """

    added_button = template.format(count, html)

    class Api:
        _window = None

        def set_window(self, window):
            self._window = window

        def close(self):
            self._window.destroy()
            self._window = None

            sys.exit(0)  # needed to prevent hang
            # return count, new_body

    api = Api()
    win = webview.create_window(title="Preview (click button to close)",
                                html=added_button,
                                js_api=api)
    api.set_window(win)
    webview.start()


if __name__ == '__main__':

    # console = rich.console.Console(width=120, force_terminal=True)

    robot = cr.CanvasRobot(reset_api_keys=False,
                           ## console=console,
                           db_update=False)

    # robot.update_database_from_canvas()
    # result = robot.get_students_dibsa('PM_MACS', local=False)
    #result = robot.search_user('u144466', 'A.J.D.Hendriks@tilburguniversity.edu')
    #result2 = robot.enroll_in_course(search="", course_id=4230, username='u144466')
    # above needs patched canvasapi
    robot.get_courses_in_account()
    robot.report_errors()
    # students_dict = robot.get_students_for_community("bauk",
    #                                                local=False)
    # robot.enroll_students_in_communities()

    # search_replace_show(robot)  # calls webview

    # del webview
    # robot.get_all_active_tst_courses(from_db=False)
    # result = robot.enroll_in_course("", 4472, 'u752058',
    # 'StudentEnrollment') #  (enrollment={}
    # user = robot.search_user('u752058')
    # print(user)
    # if not user:
    #   print(robot.errors)

    # COURSE_ID = 12594  # test course
    # foldername = 'course files/Tentamens'
    # result = robot.create_folder_in_course_files(COURSE_ID, 'Tentamens')

    # print(robot.course_metada(COURSE_ID))
    # print(robot.unpublish_folderitems_in_course(COURSE_ID,
    #                                            foldername,
    #                                            files_too=True))

    # course = robot.get_course(COURSE_ID)
    # tab = robot.get_course_tab_by_label(COURSE_ID, "Files")
    # print(tab.visibility)

    # for course_id in (10596, 10613):
    #     result = robot.create_folder_in_course_files(course_id, 'Tentamens')

    # result = robot.unpublish_subfolder_in_all_courses(foldername,
    #                                                  files_too=True,
    #                                                  check_only=True)
    # if course_ids_missing_folder:
    #    logging.info(f"Courses with missing folder
    #    {foldername}: {course_ids_missing_folder}")

    # logging.info(f"{result} folder changes and file changes")
    # logging.getLogger().setLevel(logging.INFO)
    # logging.getLogger("canvasrobot.canvasrobot").setLevel(logging.INFO)

    # 27 aug 2023
    # robot.create_folder_in_all_courses('Tentamens', report_only=False)

    # robot.create_folder_in_course_files(34, 'Tentamens')

    # QUIZZES -----------------------------
    # COURSE_ID = 10387 # course_id van Sam

    # filename = 'MP vragen Liturgie en Sacramenten.docx'
    # NUM_Q = 64
    #  ask the user? Or maybe count the numbered paragraphs, or 'a.' answers / 4
    # filename = 'Quiz_bezitter.docx'
    # filename = 'MP vragen Liturgie en Sacramenten.docx'
    # f"We are in folder {os.getcwd()}"
    # os.chdir('./data')
    # print(f"We are in folder {os.getcwd()}")
    # # robot.create_quizzes_from_document(filename=filename,
    #                                    course_id=COURSE_ID,
    #                                    question_format='Vraag {}. Vertaal:',
    #                                    adjust_fontsize=True,
    #                                    testrun=False
    #                                    )
