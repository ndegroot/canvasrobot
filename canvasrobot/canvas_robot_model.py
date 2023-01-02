from datetime import date, datetime, timedelta
import os

#try:
#    from gluon import DAL, Field, XML, HTML
#    from gluon.storage import Storage
#except ImportError:
from pydal import DAL, Field, validators
import yaml
import logging
import logging.config

from attrs import define
import keyring
import keyring.util.platform_ as keyring_platform
# for UI use rich of tkinter
from rich.prompt import Prompt
from rich.console import Console
import tkinter as tk
from tkinter import simpledialog


@define
class CanvasConfig:
    """" save the urls and API_key in a save space using keyring"""
    namespace = "canvasrobot"
    app_window: object = None
    reset_api_keys: bool = False
    url: str = ""
    api_key: str = ""
    admin_id: int = 0
    api_fields = (
        dict(msg="Enter your Canvas URL (like https://[name].instructure.com)",
             key="url"),
        dict(msg="Enter your Canvas APi Key",
             key="api_key"),
        dict(msg="Enter your Canvas Admin id",
             key="admin_id"),
    )

    # start_month = 8

    def __attrs_post_init__(self):
        if self.reset_api_keys:
            self.reset_keys()
        self.get_values()

    def get_values(self):
        """ ask for canvas api key and url , uses keyring to
        store them in a safe space"""

        values = dict()
        for field in self.api_fields:
            value = self.get_value(field["msg"], field["key"])
            self.__setattr__(field["key"], value)

    def get_value(self, msg, entry):
        value = keyring.get_password(self.namespace, entry)
        if value in (None, ""):
            value = simpledialog.askstring("Input",
                                           msg,
                                           parent=app_window) if self.app_window \
                else Prompt.ask(msg)
            keyring.set_password(self.namespace, entry, value)
            value = keyring.get_password(self.namespace, entry)
        return value

    def reset_keys(self):
        for field in self.api_fields:
            try:
                keyring.delete_password(self.namespace, field['key'])
            except keyring.errors.PasswordDeleteError:
                logging.info(f"key '{field['key']}' not found in '{self.namespace}' keyring storage")
                pass


ENROLLMENT_TYPES = {'student': 'StudentEnrollment',
                    'teacher': 'TeacherEnrollment',
                    'ta': 'TaEnrollment',
                    'observer': 'ObserverEnrollment',
                    'designer': 'DesignerEnrollment'}
EDUCATIONS = ('BANL',
              'BAUK',
              'MA',
              'PM-MA',
              'ULO',
              'PM-ULO',
              'MACS',
              'PM-MACS',
              'BIJVAK'
              )
# the 'communities-courses'


COMMUNITIES = dict(
    acskills=4485,
    theoonline=4472,
    banl=4221,
    bauk=4227,
    ma=4228,
    ulo=4229,
    macs=4230)

SHORTNAMES = dict(
    bho1=4285,
    bho2=4440,
    bho3=4441,
    theol_credo=4472,
    spirsam=7660)

STUDADMIN = ('msnijder', 'jmooij')

now = datetime.now()
# July first is considered the end of educational season
AC_YEAR = now.year - 1 if now.month < 8 else now.year
LAST_YEAR = '-{0}-{1}'.format(AC_YEAR - 1, AC_YEAR)
THIS_YEAR = '-{0}-{1}'.format(AC_YEAR, AC_YEAR + 1)
NEXT_YEAR = '-{0}-{1}'.format(AC_YEAR + 1, AC_YEAR + 2)


def load_config(default_path='ca_robot.yaml'):
    """
    Setup configuration:
    using yaml config from
    :param default_path:
    """
    path = default_path
    config = None
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
    return config


valid_roles = validators.IS_IN_SET({"T": "Teacher",
                                    "TA": "Teaching Assistant",
                                    "O": "Observer",
                                    "PS": "Proctorio Surveillant",
                                    "S": "Student"})


# noinspection PyCallingNonCallable,PyProtectedMember
class LocalDAL(DAL):
    def __init__(self, is_testing=False):
        url = 'sqlite://testing.sqlite' if is_testing else 'sqlite://storage.sqlite'
        super(LocalDAL, self).__init__(url,
                                       folder='databases',
                                       migrate=True,
                                       migrate_enabled=True,
                                       fake_migrate=False,
                                       fake_migrate_all=False)
        self.define_table('course',
                          Field('course_id', 'integer'),
                          Field('course_code', 'string'),
                          Field('sis_code', 'string'),
                          Field('ac_year', 'string'),
                          Field('name', 'string'),
                          Field('creation_date', 'date'),
                          Field('teachers', 'list:string'),  # as usernames
                          Field('teachers_names', 'list:string'),
                          Field('status', 'integer'),
                          Field('nr_modules', 'integer'),
                          Field('nr_module_items', 'integer'),
                          Field('nr_pages', 'integer'),
                          Field('nr_assignments', 'integer'),
                          Field('nr_quizzes', 'integer'),
                          Field('nr_files', 'integer'),
                          # Field('nr_collaborations', 'integer'),
                          Field('nr_ext_urls', 'integer'),
                          singular='LMS course',
                          plural='LMS courses',
                          format='%(name)s[%(teacher_names)s]')

        self.define_table('user',
                          Field('user_id', 'integer'),
                          Field('username', 'string'),
                          Field('fname', 'string'),
                          Field('first_name', 'string'),
                          Field('prefix', 'string'),
                          Field('last_name', 'string'),
                          Field('email', 'string'),
                          Field('primary_role', 'string', requires=valid_roles),
                          format='%(first_name)s %(prefix)s %(last_name)s[%(username)s]',
                          singular='User',
                          plural='Users')

        self.define_table('course2user',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'course.id',
                                                             self.course._format)),
                          Field('user',
                                'reference user',
                                requires=validators.IS_IN_DB(self, 'user.id', self.user._format)),
                          Field('role', 'string',
                                requires=valid_roles))

        # self.course.no_students = Field.Virtual('no_students',
        #                                       lambda row: self.((self.course2user.course == row.course.id) &
        #                                                         (self.course2user.role == 'S')).count())

        self.define_table('document',
                          Field('fname', 'string'),  # from bb
                          Field('info', 'string'),  # editor
                          Field('area', 'string'),  # from bb
                          Field('url', 'string'),  # from bb
                          # editor 0= unchecked 1= failed =  2: ok
                          Field('check_status', 'integer'),
                          Field('http_status', 'integer'),  # download status
                          Field('memo', 'string'),  # memo
                          # safe upload of files, keeps filenames
                          Field('bbfile', 'upload'),
                          Field('course_id', 'reference course'))
        if is_testing:
            self.truncate_all_tables()

    def truncate_all_tables(self):
        self.commit()
        for table_name in self.tables():
            self[table_name].truncate('RESTART IDENTITY CASCADE')
        self.commit()


global_config = load_config()

if logging and logging.config and global_config:
    logging.config.dictConfig(
        global_config['logging'])  # this created named loggers like 'ca_robot.cli'
