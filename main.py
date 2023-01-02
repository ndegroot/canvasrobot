import canvasrobot as cr
import rich
from rich.logging import RichHandler
import logging
import toml


if __name__ == '__main__':

    console = rich.console.Console(width=160, force_terminal=True)

    robot = cr.CanvasRobot(reset_api_keys=False)
    # todo: make ud db periodic
    robot.update_database_from_canvas()
    # robot.get_all_active_tst_courses(from_db=False)
    # result = robot.enroll_in_course("", 4472, 'u752058',
    # 'StudentEnrollment') #  (enrollment={'type': 'StudentEnrollment'}
    # user = robot.search_user('u752058')
    # print(user)
    # if not user:
    #   print(robot.errors)
    COURSE_ID = 34  # test course
    # foldername = 'course files/Tentamens'

    # print(robot.course_metada(COURSE_ID))
    # print(robot.unpublish_folderitems_in_course(COURSE_ID,
    #                                            foldername,
    #                                            files_too=True))

    course = robot.get_course(COURSE_ID)
    # tab = robot.get_course_tab_by_label(COURSE_ID, "Files")
    # print(tab.visibility)

    # for course_id in (10596, 10613):
    #     result = robot.create_folder_in_course_files(course_id, 'Tentamens')

    # result = robot.unpublish_subfolder_in_all_courses(foldername,
    #                                                  files_too=True,
    #                                                  check_only=True)
    # if course_ids_missing_folder:
    #    logging.info(f"Courses with missing folder {foldername}: {course_ids_missing_folder}")

    # logging.info(f"{result} folder changes and file changes")

    # robot.create_folder_in_all_courses('Tentamens')

    # COURSE_ID = 10387 # course_id van Sam

    # filename = 'MP vragen Liturgie en Sacramenten.docx'
    # NUM_Q = 64  #  ask the user? Or maybe count the numbered paragraphs, or 'a.' answers / 4
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
