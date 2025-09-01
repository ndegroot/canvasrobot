import logging
import sys
import shutil
from pathlib import Path
from result import is_ok, is_err, Result  # noqa: F401
from rich.prompt import Prompt
import webview
# import webview.menu as wm

from canvasrobot import SHORTNAMES


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


TEST_COURSE = 34


def search_replace_show_testcourse(cr):
    """ to check course_search_replace function dryrun, show"""
    course = cr.get_course(TEST_COURSE)
    pages = course.get_pages(include=['body'])
    search_term, replace_term = ' je', ' u'
    page_found_url = ""
    dryrun = True
    for page in pages:
        if search_term.lower() in page.body.lower():
            page_found_url = page.url  # remember
            count, replaced_body = cr.search_replace_in_page(page,
                                                             search_term=search_term,
                                                             replace_term=replace_term,
                                                             dryrun=dryrun)
            # We only need one page to test this
            if dryrun:
                show_search_result(count=count, search_term=search_term, marked_or_changed_bodies=replaced_body)
            break

    if page_found_url:
        if not dryrun:
            # read again from canvas instance to check
            page = course.get_page(page_found_url)
            assert search_term not in page.body
            assert replace_term in page.body
    else:
        assert False, f"Source string '{search_term}' not found in any page of course {TEST_COURSE}"


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


def show_search_result(count: int = 0,
                       search_term: str = "",
                       found_pages: list = None,
                       marked_or_changed_bodies: str = "",
                       canvas_url: str = None):
    """in webview show result for search or replace with links
    show
    - count of search locations
    - list of pages with page-links"""

    page_links = [(f"<li><a href='{canvas_url}/courses/{course_id}/pages/{url}' "
                   f"target='_blank'>{title} in {course_name}"
                   f"</a></li>") for course_id, course_name, url, title in found_pages]
    page_list = f"<ul>{''.join(page_links)}</ul>"

    report = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Zoekresultaat</title>
      
    </head>
    <body>
      <p>Below the {count} found and marked (>{search_term}<) locations in the pages:</p>
      {page_list}
      <button onclick='pywebview.api.close()'> Close </button>
      <hr/>
      {marked_or_changed_bodies}  
    </body>
    </html>
    """
    # https://tilburguniversity.instructure.com/courses/34/wiki

    api = WebviewApi()
    win = webview.create_window(title="Preview (click [Close] button to close)",
                                html=report,
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
    webview.settings = {
        'ALLOW_DOWNLOADS': False,  # Allow file downloads
        'ALLOW_FILE_URLS': True,  # Allow access to file:// urls
        'OPEN_EXTERNAL_LINKS_IN_BROWSER': True,  # Open target=_blank links in an external browser
        'OPEN_DEVTOOLS_IN_DEBUG': True,  # Automatically open devtools when `start(debug=True)`.
    }
    webview.start(debug=True)


def overview_courses(courses, canvas_url: str = None):
    """in webview show list of courses with ids and links"""

    course_links = [(f"<tr><td>{course.id}</td><td>"
                     f"<a href='{canvas_url}/courses/{course.id}' "
                     f"target='_blank'>{course.name}</a></td></tr>") for course in courses]
    course_list = f"<table class='sortable-theme-bootstrap' data-sortable>{''.join(course_links)}</table>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Cursussen</title>
      <script src="sortable-0.8.0/js/sortable.min.js"></script>
      <link rel="stylesheet" href="sortable-0.8.0./css/sortable-theme-bootstrap.css" />
    </head>
    <body>
      <h2>{len(courses)} courses</h1>
      <button onclick='pywebview.api.close()'> Close </button>
      <hr/>
      {course_list}
    </body>
    </html>
    """
    # format: https://tilburguniversity.instructure.com/courses/34/wiki

    api = WebviewApi()
    win = webview.create_window(
                                # "index.html",
                                title="Preview (click [Close] button to close)",
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
def enroll_student(robot, username, shortname, unenroll=False,):
    """
    Enroll a student in a predetermined course.
    This function uses placeholder values for demonstration.
    """
    course_url = robot.canvas_url+"/courses/{}"
    course_id = SHORTNAMES.get(shortname, None)

    if not course_id:
        robot.console.print(f"Course '{shortname}' not found in SHORTNAMES.")
        return

    if unenroll:
        result = robot.unenroll_in_course(
            course_id,
            username,
            enrollment={}
        )
        if is_ok(result):
            href = course_url.format(course_id)
            robot.console.print(
                f"'{username} is verwijderd als student aan de cursus '{shortname}' link: {href}")
        else:
            robot.console.print(
                f"'{result.value.name} is NIET verwijderd als student aan de cursus '{shortname}'")
        return result

    result = robot.enroll_in_course(
            course_id=course_id,
            username=username,
            enrollment={})

    if is_ok(result):
        href = course_url.format(course_id)
        robot.console.print(f"'{username} is toegevoegd als student aan de cursus '{shortname}' link: {href}")
    if is_err(result):
        robot.console.print(f"'{result.value}': "
                            f"'{username}' is niet toegevoegd aan '{shortname}'")


def search_in_course(robot, single_course=0, dryrun=True, ignore_case=True):
    """cmdline: ask for search and replace term. Scope: one course, all pages"""
    robot.console.print("Zoek tekstfragment in een cursus")
    search_only = Prompt.ask("Alleen zoeken?",
                             choices=["zoek", "vervang"],
                             default="zoek",
                             show_default=True)
    search_only = True if search_only == "zoek" else False
    while True:
        search_term = Prompt.ask("Voer de zoekterm in")
        if len(search_term) > 1:
            break
        robot.console.print("Voer een langere zoekterm in")
    replace_term = Prompt.ask("Voer vervangterm in") if not search_only else ""
    course_id = Prompt.ask("Voer de course_id in") if single_course == 0 else single_course
    robot.console.print('Zoeken..')
    count, found_pages, marked_bodies = robot.course_search_replace_pages(course_id,
                                                                          search_term=search_term,
                                                                          replace_term=replace_term,
                                                                          search_only=search_only,
                                                                          ignore_case=ignore_case,
                                                                          dryrun=dryrun)
    show_search_result(count=count,
                       search_term=search_term,
                       found_pages=found_pages,
                       marked_or_changed_bodies=marked_bodies,
                       canvas_url=robot.canvas_url)
    return count, found_pages, marked_bodies


def search_in_courses(robot, dryrun=True, ignore_case=True):
    """cmdline: ask for search and replace term. Scope: all courses, all pages"""
    robot.console.print("Zoek tekstfragment in alle cursussen")
    search_only = Prompt.ask("Alleen zoeken?",
                             choices=["zoek", "vervang"],
                             default="zoek",
                             show_default=True)
    search_only = True if search_only == "zoek" else False
    search_term = Prompt.ask("Voer de zoekterm in")
    replace_term = Prompt.ask("Voer vervangterm in") if not search_only else ""
    robot.console.print('Zoeken..')
    count, found_pages, marked_bodies = robot.course_search_replace_pages_all_courses(search_term=search_term,
                                                                                      replace_term=replace_term,
                                                                                      search_only=search_only,
                                                                                      ignore_case=ignore_case,
                                                                                      dryrun=dryrun)
    show_search_result(count=count,
                       search_term=search_term,
                       found_pages=found_pages,
                       marked_or_changed_bodies=marked_bodies,
                       canvas_url=robot.canvas_url)
    return count, found_pages, marked_bodies


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
    count, found_pages, html = robot.course_search_replace_pages(course_id,
                                                                 search_term,
                                                                 replace_term,
                                                                 search_only)
    show_search_result(count=count,
                       search_term=search_term,
                       found_pages=found_pages,
                       marked_or_changed_bodies=html,
                       canvas_url=robot.canvas_url)
