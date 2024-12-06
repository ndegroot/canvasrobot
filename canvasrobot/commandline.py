import logging
import sys
import shutil
from pathlib import Path
from typing import Type
from result import is_ok, is_err, Result
import rich
from rich.prompt import Prompt
import rich_click as click
import webview
import webview.menu as wm

from canvasrobot import CanvasRobot, SHORTNAMES


class DatabaseLocationError(Exception):
    pass


def search_replace_show(cr):
    """ check course_search_replace function dryrun, show"""
    course = cr.get_course(TEST_COURSE)
    pages = course.get_pages(include=['body'])
    search_text, replace_text = ' je', ' u'
    page_found_url = ""
    dryrun = True
    for page in pages:
        if search_text in page.body:
            page_found_url = page.url  # remember
            count, replaced_body = cr.search_replace_in_page(page, search_text, replace_text,
                                                             dryrun=dryrun)
            # We only need one page to test this
            if dryrun:
                show_search_result(count,[],html)
            break

    if page_found_url:
        if not dryrun:
            # read again from canvas instance to check
            page = course.get_page(page_found_url)
            assert search_text not in page.body
            assert replace_text in page.body
    else:
        assert False, f"Source string '{search_text}' not found in any page of course {TEST_COURSE}"


class WebviewApi:

    _window = None

    def set_window(self, window):
        self._window = window

    def close(self):
        self._window.destroy()
        self._window = None

        sys.exit(0)  # needed to prevent hang
        # return count, new_body


def change_active_window_content():
    active_window = webview.active_window()
    if active_window:
        active_window.load_html('<h1>You changed this window!</h1>')


def click_me():
    active_window = webview.active_window()
    if active_window:
        active_window.load_html('<h1>You clicked me!</h1>')


def do_nothing():
    pass


def show_search_result(count: int, found_pages: list, html: str, canvas_url: str = None):
    """in webview show result for search-replace with links"""

    template = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Zoekresultaat</title>
      
    </head>
    <body>
      <p>In <span style='color: red;' >red</span> below the {} found locations in </p>
      {}
      <button onclick='pywebview.api.close()'>Klaar</button>
      <hr/>
      {}  
    </body>
    </html>
    """
    # https://tilburguniversity.instructure.com/courses/34/wiki

    page_links = [f"<li><a href='{canvas_url}/courses/{course_id}/pages/{url}' target='_blank'>{title} in {course_name}</a></li>" for course_id, course_name, url, title in found_pages]
    page_list = f"<ul>{''.join(page_links)}</ul>"
    added_button = template.format(count, page_list, html)

    api = WebviewApi()
    win = webview.create_window(title="Preview (click button to close)",
                                html=added_button,
                                js_api=api)
    api.set_window(win)
#     menu_items = [wm.Menu('Test Menu',
#                           [wm.MenuAction('Change Active Window Content',
#                                                change_active_window_content),
#                                  wm.MenuSeparator(),
#                                  wm.Menu('Random',
#                                          [ wm.MenuAction('Click Me',
#                                                                 click_me),
# #                               wm.MenuAction('File Dialog', open_file_dialog),
#                                                 ],
#                                          ),
#                                 ],
#                           ),
#                   wm.Menu('Nothing Here',
#                           [wm.MenuAction('This will do nothing', do_nothing)]
#                           ),
#                  ]
    webview.start()


def overview_courses(courses, canvas_url: str = None):
    """in webview show list of course with ids and links"""

    template = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Cursussen</title>
      <script src="sortable-0.8.0/js/sortable.min.js"></script>
      <link rel="stylesheet" href="sortable-0.8.0./css/sortable-theme-bootstrap.css" />
    </head>
    <body>
      <h2>{} courses</h1>
      <button onclick='pywebview.api.close()'>Klaar</button>
      <hr/>
      {}
    </body>
    </html>
    """
    # format: https://tilburguniversity.instructure.com/courses/34/wiki
    course_links = [(f"<tr><td>{course.id}</td><td>"
                     f"<a href='{canvas_url}/courses/{course.id}' "
                     f"target='_blank'>{course.name}</a></td></tr>") for course in courses]
    course_list = f"<table class='sortable-theme-bootstrap' data-sortable>{''.join(course_links)}</table>"
    html = template.format(len(courses), course_list)

    api = WebviewApi()
    win = webview.create_window(
                                # "index.html",
                                title="Preview (click button to close)",
                                html=html,
                                js_api=api)
    api.set_window(win)
    webview.start(debug=True)


def get_logger(logger_name='canvasrobot'):

    logger = logging.getLogger("canvasrobot.canvasrobot")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(f"{logger_name}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.WARNING)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(logging.INFO)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


def enroll_student(robot):
    """enroll student in a course"""
    course_url = robot.canvas_url+"/courses/{}"
    choices = SHORTNAMES.keys()
    robot.console.print("Voeg een account toe aan een Canvas cursus")
    login = Prompt.ask("Voer de inlognaam in")
    choice = Prompt.ask(
        "Maak een keuze uit de volgende cursussen",
        choices=choices,
        show_choices=True
    )
    course_id = SHORTNAMES[choice]

    result = robot.enroll_in_course(
            course_id=course_id,
            username=login,
            enrollment={})

    if is_ok(result):
        href = course_url.format(course_id)
        robot.console.print(f"{result.value.name} toegevoegd aan de cursus '{choice}' link: {href}")
    if is_err(result):
        robot.console.print(f"Fout: '{result.value}', '{login}' is niet toegevoegd aan '{choice}'")


def search_course(robot, single_course=0):
    """cmdline: ask for search and replace term. Scope one course all pages"""
    robot.console.print("Zoek tekstfragment in een cursus")
    search_only = Prompt.ask("Alleen zoeken?",
                             choices=["zoek", "vervang"],
                             default="zoek",
                             show_default=True)
    search_only = True if search_only == "zoek" else False
    search_term = Prompt.ask("Voer de zoekterm in")
    replace_term = Prompt.ask("Voer vervangterm in") if not search_only else ""
    course_id = Prompt.ask("Voer de course_id in") if single_course == 0 else single_course
    robot.console.print('Zoeken..')
    count, found_pages, html = robot.course_search_replace_pages(course_id, search_term, replace_term, search_only)
    show_search_result(count, found_pages, html, robot.canvas_url)


def search_courses(robot):
    """cmdline: ask for search and replace term. Scope: all courses"""
    robot.console.print("Zoek tekstfragment in alle cursussen")
    search_only = Prompt.ask("Alleen zoeken?",
                             choices=["zoek", "vervang"],
                             default="zoek",
                             show_default=True)
    search_only = True if search_only == "zoek" else False
    search_term = Prompt.ask("Voer de zoekterm in")
    replace_term = Prompt.ask("Voer vervangterm in") if not search_only else ""
    robot.console.print('Zoeken..')
    count, found_pages, html = robot.course_search_replace_pages_all_courses(search_term, replace_term, search_only)
    show_search_result(count, found_pages, html, robot.canvas_url)


def search_replace_pages(robot, single_course=0):
    """cmdline: ask for search and replace term and scope"""
    robot.console.print("Zoek (en vervang) een tekstfragment in een cursus")
    search_only = Prompt.ask("Alleen zoeken?",
                             choices=["zoek", "vervang"],
                             default="zoek",
                             show_default=True)
    search_only = True if search_only == "zoek" else False
    search_term = Prompt.ask("Voer de zoekterm in")
    replace_term = Prompt.ask("Voer vervangterm in") if not search_only else ""
    course_id = Prompt.ask("Voer de course_id in") if single_course == 0 else single_course
    count, found_pages, html = robot.course_search_replace_pages(course_id, search_term, replace_term, search_only)
    show_search_result(count, found_pages, html, robot.canvas_url)


@click.command("CanvasRobot",
               no_args_is_help=True,
               epilog='Check out our docs at https://click.palletsprojects.com/ for more details')
@click.option("--reset_api_keys",
              default=False,
              is_flag=True,
              help="Update your canvas URL, Canvas API key, and admin id")
@click.option("--db_auto_update",
              default=False,
              is_flag=True,
              help="If supplied: automatic database updates.")
@click.option("--db_force_update",  # Working
              default=False,
              is_flag=True,
              help="If supplied: force database update.")
@click.option("--do",
              type=click.Choice([
                  'enroll_student',  # working
                  'search_course',
                  'search_all',
                  'replace',
                  'get_courses',
                  'enroll_students_in_communities',
                  'show_courses']),
              help='Choose a command to run'
              )
def run(reset_api_keys, db_auto_update, db_force_update, do):

    path = create_db_folder()

    robot = CanvasRobot(reset_api_keys=reset_api_keys,
                        db_auto_update=db_auto_update,
                        db_force_update=db_force_update,
                        db_folder=path,)

    # canvas_url = robot.canvas_url
    # robot.update_database_from_canvas()
    # result = robot.get_students_dibsa('PM_MACS', local=False)
    # result = robot.search_user('u144466', 'A.J.D.Hendriks@tilburguniversity.edu')
    # result2 = robot.enroll_in_course(search="", course_id=4230, username='u144466')
    # above needs patched canvasapi

    match do:
        case 'show_courses':
            courses = robot.get_courses_in_account()
            overview_courses(courses, robot.canvas_url)

        case 'enroll_student':
            enroll_student(robot)
        case 'search_course':
            search_course(robot)
        case 'search_all':
            search_courses(robot)
        case 'enroll_students_in_communities':
            robot.enroll_students_in_communities()

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


def create_db_folder():
    """create and return db folder & put asset there"""
    def go_up(path, levels=1):
        path = Path(path)
        for _ in range(levels):
            path = path.parent
        return path

    path = Path(__file__)  # inside canvasrobot folder
    # /Users/ncdegroot/.local/share/uv/tools/canvasrobot/lib/python3.13/site-packages/canvasrobot/databases
    if "uv" in path.parts:
        # running as an uv tool
        npath = go_up(path, levels=5)
        npath = npath / "database"
        npath.mkdir(exist_ok=True)
        asset = path.parent / "assets" / "redirect_list.xlsx"
        shutil.copy(asset, npath)
        return npath

    else:
        # inside project folder (pycharm)
        path = Path.home() / "databases" / "canvasrobot"
        path.mkdir(exist_ok=True)
        return path


if __name__ == '__main__':
    run()
    # console = rich.console.Console(width=120, force_terminal=True)
