import re
import os
import sys
import pathlib
from pathlib import Path
import logging
import sqlite3
import openpyxl
import webview
from attrs import define
import rich_click as click

from result import Ok, Err, Result, is_ok, is_err
from canvasrobot import CanvasRobot, Field
from .commandline import create_db_folder, get_logger


logger = get_logger("urltransform")


def replace_and_count(original_string: str,
                      search_string: str,
                      replace_string: str,
                      dryrun=False) -> (str, int):
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
      <title>Zoekresultaat</title>
    </head>
    <body>
      <h2>Mediasite urls without replacement:</h2>
      <p>Klik op de link(s) om de pagina te openen.</p>
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


class UrlTransformationRobot(CanvasRobot):
    con = None
    cr = None
    current_page = None
    current_page_url = None
    transformation_report = ""
    pages_changed = 0
    count_replacements = 0

    def __init__(self, db_folder=None,
                 is_testing=False,
                 db_auto_update=False,
                 db_force_update=False):
        super().__init__(db_folder=db_folder,
                         is_testing=is_testing,
                         db_no_update=db_no_update,
                         db_force_update=db_force_update)
        self.add_media_ids_table()
        if self.db(self.db.ids).isempty():
            self.import_ids()

    # Begin database section
    def add_media_ids_table(self):
        self.db.define_table('ids',
                             Field('panopto_id', 'string'),
                             Field('mediasite_id', 'string'))

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
        """read ids table from spreadsheet"""
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

    def lookup_panopto_id(self, mediasite_id: str) -> str:
        db = self.db  # just sugarcoat
        row = db(db.ids.mediasite_id == mediasite_id).select(db.ids.panopto_id).first()
        return row.panopto_id if row else None

    # End database section

    def mediasite2panopto(self, text: str, dryrun=False) -> (str, bool):
        """
        :param text possibly with mediasite urls
        :param dryrun: if true just statistics, no action
        :returns text with updated urls if panopto id are found in lookup
        replace the ms_id with p_id in the
        https://videocollege.uvt.nl/Mediasite/
        Play/ce152c1602144b80bad5a222b7d4cc731d
        replace by (redirect procedure until dec 2024)
        https://tilburguniversity.cloud.panopto.eu/Panopto/Pages/
        Viewer.aspx?id=221a5d47-84ea-44e1-b826-af52017be85c
        """
        updated = False
        updated_text = text
        count_replacements = 0
        # match each source-url and extract the id into a  list of ms_ids
        matches = re.findall(r'(https://videocollege\.uvt\.nl/Mediasite/Play/([a-z0-9]+))', text)

        # for each ms_id: lookup p_id and construct new target-url
        for match in matches:
            ms_url = match[0]
            ms_id = match[1]
            pn_id = self.lookup_panopto_id(ms_id)
            if pn_id:
                # replace source-url with target-url
                pn_url = PN_URL % pn_id
                updated_text, count = replace_and_count(text, ms_url, pn_url, dryrun=dryrun)
                count_replacements += count
                updated = True
            else:
                # no corresponding panopto id found in dv
                msg = (f"<a href={self.current_page_url} target='_blank'>{self.current_page}</a>"
                       f" has mediasite url {ms_url} which is NOT transformed "
                       f"because the mediasite id is not found in DB.")
                logger.info(msg)
                self.transformation_report += (msg + '<br/>')
        return updated_text, updated, count_replacements

    def transform_pages_in_course(self, course_id: int, dryrun=False):
        """
        Transform the mediasite urls in all pages of the course with this course_id
        :param course_id:
        :param dryrun: if true just statistics
        :return:
        """
        pages = self.course_get_pages(course_id)  # example
        for page in pages:
            if page.body:
                self.current_page_url = page.html_url
                self.current_page = page.title
                new_body, updated, count = self.mediasite2panopto(page.body)
                self.count_replacements += count
                if updated:
                    self.pages_changed += 1
                    if not dryrun:
                        page.edit(wiki_page=dict(body=new_body))
        return


@define
class TestCourse:
    id: int


def go_up(path, levels=1):
    path = Path(path)
    for _ in range(levels):
        path = path.parent
    return path


@click.command()
@click.option("--dryrun", default=True, is_flag=True,
              help="If given only show *possible* result.")
@click.option("--single_course", default=0,
              help="Give Canvas id of a single course.")
@click.option("--db_no_update", default=True, is_flag=True,
              help="Don't update.")
@click.option("--db_force_update", default=False, is_flag=True,
              help="Force db update. Otherwise periodic.")
@click.option("--stop_after", default=0, help="Stop after this many courses.")
def run(dryrun, single_course, db_no_update, db_force_update,
        stop_after):

    path = create_db_folder()
    tr = UrlTransformationRobot(db_no_update=db_no_update,
                                db_force_update=db_force_update,
                                db_folder=path)  # default location db: folder 'databases'

    courses = (TestCourse(single_course),) if single_course else tr.get_courses_in_account()
    index = 0
    for index, course in enumerate(courses):
        if stop_after and index > stop_after:
            break
        tr.transform_pages_in_course(course.id, dryrun=dryrun)
    tr.transformation_report += (f"<p>{index} courses checked.</p>"
                                 f"<p>{tr.pages_changed} "
                                 f"{'pages would be changed' if dryrun else 'pages were changed'},"
                                 f" {tr.count_replacements} urls "
                                 f"{'would be' if dryrun else ''} replaced</p>")
    if tr.transformation_report:
        show_result(tr.transformation_report)
    tr.report_errors()


if __name__ == '__main__':
    run()
