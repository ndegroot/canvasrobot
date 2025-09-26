import re
import sys
import typing
import operator
from pathlib import Path
import logging
from pydal.objects import Row
import openpyxl
import webview
from attrs import define
import rich_click as click

from result import Ok, Err, Result, is_err
from canvasrobot import CanvasRobot, Field
import canvasapi
from .commandline import create_db_folder, get_logger


MS_URL = "https://videocollege.uvt.nl/Mediasite/Play/%s"
PN_URL = "https://tilburguniversity.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=%s"

# logger = logging.getLogger(__name__)
logger = get_logger("urltransform",
                    file_level=logging.DEBUG)
logger.setLevel(logging.INFO)


def replace_and_count(original_string: str,
                      search_string: str,
                      replace_string: str,
                      dryrun=False) -> tuple[str, int]:
    count = 0
    processed_string = original_string
    while search_string in processed_string:
        processed_string = processed_string.replace(search_string, replace_string, 1)
        count += 1
    return original_string if dryrun else processed_string, count


def show_result(html: str):

    template = """
    <!DOCTYPE html>
    <html>
    <head>
      <title>Search Results</title>
    </head>
    <body>
      <h2>Pages with Mediasite URLs</h2>
      <p>Use the link(s) to check the pages or video URLs.</p>
      <hr/>
      {}
      <hr/>
      <button onclick='pywebview.api.close()'>Sluit</button>
    </body>
    </html>
    """

    html_with_ui = template.format(html)

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
    win = webview.create_window(title="Error report (click button to close)",
                                html=html_with_ui,
                                js_api=api)
    api.set_window(win)
    webview.start()


class ImportExcelError(Exception):
    pass


@define
class TransformedPage:
    list: typing.ClassVar[list] = []
    title: str
    url: str

    def __attrs_post_init__(self):
        TransformedPage.list.append(self)

    @classmethod
    def get_list(cls):
        return cls.list

    @classmethod
    def clear_list(cls):
        cls.list = []

    @classmethod
    def get_column(cls, field):
        attr_of = operator.attrgetter(field)
        # the_list = cls.get_list()
        return list(map(attr_of, cls.list))


class MixinMediasite2Panopto:
    def add_media_ids_table(self):
        self.db.define_table('ids',
                             Field('panopto_id', 'string'),
                             Field('mediasite_id', 'string'))

    def lookup_panopto_id(self, mediasite_id: str) -> str:
        db = self.db  # just sugarcoat
        row = db(db.ids.mediasite_id == mediasite_id).select(db.ids.panopto_id).first()
        return row.panopto_id if row else None

    def mediasite2panopto(self, text: str, dryrun=True) -> tuple[str, bool, int]:
        """
        Replace links in a single page or other item with text
        :param text possibly with mediasite urls
        :param dryrun: if true just statistics, no action
        :returns tuple with
        1. text with transformed mediasite urls if panopto id are found in lookup (unless dryrun)
        2. flag True if updates were made
        3. count of replacements made
        (replace the ms_id with p_id in the
        https://videocollege.uvt.nl/Mediasite/
        Play/ce152c1602144b80bad5a222b7d4cc731d
        replace by (redirect procedure until dec 2024)
        https://tilburguniversity.cloud.panopto.eu/Panopto/Pages/
        Viewer.aspx?id=221a5d47-84ea-44e1-b826-af52017be85c)
        """
        updated = False
        updated_text = text
        count_replacements = 0
        # match each source-url and extract the id into a list of ms_ids
        matches = re.findall(r'(https://videocollege\.uvt\.nl/Mediasite/Play/([a-z0-9]+))', text)

        if num_matches := len(matches):
            logger.debug(f"{num_matches} 'videocollege-url' matches in {self.current_page} {self.current_page_url}")

        msg = (f"<p><a href={self.current_page_url} target='_blank'>"
               f" Open page '{self.current_page}'</a></p>")
        # for each ms_id: look up p_id and construct a new target-url
        action_or_not = 'would become' if dryrun else 'changed into'
        for match in matches:
            ms_url = match[0]
            ms_id = match[1]
            pn_id = self.lookup_panopto_id(ms_id)
            if pn_id:
                # replace source-url with target-url
                pn_url = PN_URL % pn_id

                logger.debug(f"'{ms_url}' {action_or_not} '{pn_url}' in {self.current_page_url}")

                updated_text, count = replace_and_count(text, ms_url, pn_url, dryrun=dryrun)

                logger.debug(f"{count} occurrences {action_or_not} in '{updated_text}' from {self.current_page_url}")
                msg += (f"<p><a href={ms_url} target='_blank'>{ms_url}</a>"
                        f" {action_or_not} <a href={pn_url} target='_blank'>{pn_url}</a></p>")

                count_replacements += count
                updated = True
            else:
                # no corresponding panopto id found in dv
                msg += (f"<p>Page "
                        f" has mediasite url {ms_url} which could NOT be transformed "
                        f"because the mediasite id is not found in DB.</p>")

                logger.warning(f"Mediasite_id {ms_id} not found {self.current_page} {self.current_page_url} {ms_id}")
            self.transformation_report += (msg + '<br/>')
            logger.debug(f"{count_replacements} candidates in {self.current_page} {self.current_page_url} ")

        return updated_text, updated, count_replacements

    def import_ids(self):

        ids_result = self.get_video_ids()
        if is_err(ids_result):
            raise ImportExcelError(ids_result.err_value)

        rows = ids_result.ok_value
        print(rows[0])
        assert rows[0]['PanoptoID'] == '532f98ad-43dc-45b6-8109-aeeb01865f0e', \
            "import error in db"
        for row in rows:
            self.db.ids.insert(mediasite_id=row['MediasiteID'],
                               panopto_id=row['PanoptoID'])
        self.db.commit()

    def get_video_ids(self) -> Result[list[dict[str, str]], str]:
        """read id table from the spreadsheet"""
        xls_path = self.db_folder / "redirect_list.xlsx"
        try:
            sh = openpyxl.load_workbook(xls_path).active
            column_names = next(sh.values)[0:]
            # Initialize the list of dictionaries
            rows_as_dicts = []
            # Iterate over the sheet rows (excluding header)
            for row in sh.iter_rows(min_row=2, values_only=True):
                row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
                rows_as_dicts.append(row_dict)
            return Ok(rows_as_dicts)
        except Exception as e:
            msg = f"Error opening exported video ID list({e})"
            return Err(msg)


class UrlTransformationRobot(CanvasRobot, MixinMediasite2Panopto):
    con = None
    cr = None
    current_page = None
    current_page_url = None
    # current_transformed_pages: list[TransformedPage] = []
    transformation_report = ""
    pages_changed = 0
    count_replacements = 0

    def __init__(self, db_folder: Path = None,
                 is_testing: bool = False,
                 db_auto_update: bool = False,
                 db_force_update: bool = False):
        super().__init__(db_folder=db_folder,
                         is_testing=is_testing,
                         db_auto_update=db_auto_update,
                         db_force_update=db_force_update)
        self.add_media_ids_table()
        if self.db(self.db.ids).isempty():
            self.import_ids()

    def save_transform_data_db(self, course_id: int = None):

        course = self.canvas.get_course(course_id)

        c_id = self.update_db_for(course, single_course=course_id)
        # course needs to be present in the course table for course2user

        db = self.db

        teacher_names, teacher_logins, teacher_ids = self.update_db_teachers(course)

        # make a relational link between course-user(teacher)
        for teacher_id in teacher_ids:
            _ = db.course2user.update_or_insert((db.course2user.user == teacher_id) &
                                                (db.course2user.course == course_id),
                                                user=teacher_id,
                                                course=c_id,
                                                role='T')
        transformed_page_titles = TransformedPage.get_column('title')
        _ = db.course_urltransform.update_or_insert(
            (db.course_urltransform.course_id == course_id),
            course_id=course_id,
            teacher_logins=teacher_logins,
            nr_pages=len(transformed_page_titles),
            page_titles=transformed_page_titles,
            page_urls=TransformedPage.get_column('url'),
            module_items=[0,],
            dryrun=TransformedPage.dryrun
            # todo: modules

        )
        db.commit()
        pass

    def get_transform_data(self, course_id: int) -> Row | None:
        """ get (candidate if row.dryrun) transform data
        :param course_id:
        :returns db row or None if not found"""
        db = self.db
        # todo: maybe optionally join with db.course/ db.user ?
        row = db(db.course_urltransform.course_id == course_id).select(db.course_urltransform.ALL).first()
        return row

    def transform_pages_in_course(self, course_id: int, dryrun=True) -> bool:
        """
        Transform the mediasite urls in all pages of the course with this course_id
        :param course_id:
        :param dryrun: if true, take no actions, show predictions
        :return: True unless error
        """
        logger.debug(f"Getting pages from course {course_id}")
        try:
            pages = self.course_get_pages(course_id)  # example

        except (Exception, canvasapi.exceptions.Forbidden) as e:
            err = f"Course {course_id} skipped due to {e}"
            logger.warning(err)
            self.errors.append(err)
            return False
        else:
            TransformedPage.clear_list()
            TransformedPage.dryrun = dryrun
            for page in pages:
                logger.debug(f"Handling '{page.title}'")
                if page.body:
                    self.current_page_url = page.html_url
                    self.current_page = page.title
                    new_body, updated, count = self.mediasite2panopto(page.body, dryrun=dryrun)
                    self.count_replacements += count
                    if updated:
                        _ = TransformedPage(page.title, page.html_url)  # build list
                        self.pages_changed += 1
                        if not dryrun:
                            # actual replacement
                            page.edit(wiki_page=dict(body=new_body))
            self.save_transform_data_db(course_id)  # uses the page list in TransformedPage
        return True


@define
class TestCourse:
    id: int


def go_up(path, levels=1):
    path = Path(path)
    for _ in range(levels):
        path = path.parent
    return path


@click.command()
@click.pass_context
@click.option("--dryrun/--do_it", default=True, is_flag=True,
              help="Only show *possible* results, no changes unless --do_it is given instead.")
@click.option("--single_course", default=0,
              help="Give Canvas id of a single course.")
@click.option("--db_auto_update", default=False, is_flag=True,
              help="Don't update the database automatically.")
@click.option("--db_force_update", default=False, is_flag=True,
              help="Force db update. Otherwise periodic.")
@click.option("--stop_after", default=0, help="Stop after this many courses.")
@click.version_option()
def cli(ctx, dryrun, single_course, db_auto_update, db_force_update,
        stop_after):
    if ('single_course' not in ctx.params.keys() and
            click.confirm("Continue handling all courses?")):
        click.echo("Aborted!")
        return
    if dryrun:
        click.echo("Just a dryrun, no changes to the pages.")
    path = create_db_folder()
    tr = UrlTransformationRobot(db_auto_update=db_auto_update,
                                db_force_update=db_force_update,
                                db_folder=path)  # default location db: folder 'databases'

    courses = (TestCourse(single_course),) if single_course else tr.get_courses_in_account()
    index = 0
    for index, course in enumerate(courses, start=1):
        if stop_after and index > stop_after:
            break
        tr.transform_pages_in_course(course.id, dryrun=dryrun)

    # conclusion
    tr.transformation_report += (f"<p>{index} course{'s' if index == 1 else ''} checked.</p>"
                                 f"<p>{tr.pages_changed} "
                                 f"{'pages would be changed' if dryrun else 'pages were changed'},"
                                 f" {tr.count_replacements} urls "
                                 f"{'would be' if dryrun else ''} replaced</p>")
    if tr.transformation_report:
        show_result(tr.transformation_report)
    tr.report_errors()


if __name__ == '__main__':
    cli()
