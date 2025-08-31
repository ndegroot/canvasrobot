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


# util functions ######################
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
                show_search_result(count, [], html)
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

    page_links = [(f"<li><a href='{canvas_url}/courses/{course_id}/pages/{url}' target='_blank'>{title} in {course_name}"
                   f"</a></li>") for course_id, course_name, url, title in found_pages]
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


def load_css(window):
    window.load_css(
        """
    table
    {
        width: 100 %;
        table-layout: fixed;
    }
    .filename
    {
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        width: 60%;
        max-width: 60%;
    }
    .url
    {
        width: 15%;
        text-align: right;
        padding-right: 4px;
    }
    .course{
        width: 15%;
        text-align: right;
    }
    """
    )


def overview_documents(rows, canvas_url: str = None):
    """in webview show list of documents with ids and links"""

    template = """
    <!DOCTYPE html>
    <html>
    <head>
      <meta charset="UTF-8">
      <title>Bestanden</title>
      <script src="sortable-0.8.0/js/sortable.min.js"></script>
      <link rel="stylesheet" href="sortable-0.8.0./css/sortable-theme-bootstrap.css" />
     <style type="text/css">
     .files{{
        width: 100%;
        table-layout: fixed;
     }}
     .filename{{
        text-overflow: ellipsis;
        white-space: nowrap;
        overflow: hidden;
        width: 40%;
        max-width: 40%;
    }}
    .url{{
        width: 20%;
        text-align: right;
        padding-right: 4px;
    }}
    .course{{
        width: 40%;
        text-align: right;
    }}
     
    </style> 
    </head>
    <body>
      <h2>{} bestanden</h1>
      <button onclick='pywebview.api.close()'>Klaar</button>
      <hr/>
      {}
    </body>
    </html>
    """
    # format: https://tilburguniversity.instructure.com/courses/34/wiki
    doc_links = [(f"<tr><td class='filename'>{row.document.filename}</td><td class='url'>"
                  f"<a href='{row.document.url}' "
                  f"target='_blank'>{row.document.id}</a></td><td class='course'>"
                  f"<a href='{canvas_url}/courses/{row.course.course_id}' "
                  f"target='_blank'>{row.course.name}</a></td>"
                  f"</tr>") for row in rows]
    doc_list = f"<table class='files sortable-theme-bootstrap data-sortable'>{''.join(doc_links)}</table>"
    html = template.format(len(rows), doc_list)

    api = WebviewApi()
    win = webview.create_window(
        # "index.html",
        title="Preview (click button to close)",
        html=html,

        js_api=api)
    api.set_window(win)
    # webview.start(load_css, win, debug=True)
    webview.start(debug=True)


def get_logger(logger_name='canvasrobot',
               file_level=logging.WARNING,
               stream_level=logging.INFO):

    logger = logging.getLogger("canvasrobot.canvasrobot")
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
    file_handler = logging.FileHandler(f"{logger_name}.log")
    file_handler.setFormatter(formatter)
    file_handler.setLevel(file_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    stream_handler.setLevel(stream_level)

    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)

    return logger


# commands
def enroll_student(robot):
    """
    Enroll a student in a predetermined course.
    This function uses placeholder values for demonstration.
    """
    course_url = robot.canvas_url+"/courses/{}"
    login = 'student_login'  # Placeholder for user login name
    choice = 'course_choice'  # Placeholder for course choice
    course_id = SHORTNAMES.get(choice, None)

    if not course_id:
        robot.console.print(f"Course '{choice}' not found in SHORTNAMES.")
        return

    result = robot.enroll_in_course(
            course_id=course_id,
            username=login,
            enrollment={})

    if is_ok(result):
        href = course_url.format(course_id)
        robot.console.print(f"{result.value.name} toegevoegd aan de cursus '{choice}' link: {href}")
    if is_err(result):
        robot.console.print(f"Fout: '{result.value}', '{login}' is niet toegevoegd aan '{choice}'")


def search_in_course(robot, single_course=0):
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


def search_in_courses(robot):
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
