from datetime import datetime
import os
from typing import Optional, NewType
from pydal import DAL, Field, validators  # type: ignore
import yaml
import logging
import logging.config
from attrs import define
import keyring
# for UI use rich or tkinter
from rich.prompt import Prompt
from tkinter import simpledialog

# from entities import Course

# Custom type definitions
CourseId = NewType('CourseId', int)
CourseLanguage = NewType('CourseLanguage', str)
CommunityName = NewType('CommunityName', str)
SubcommunityName = NewType('SubcommunityName', str)
SubcommunityDict = NewType("SubcommunityDict", dict[SubcommunityName, tuple[CourseId | None, CourseLanguage]])
CommunityDict = NewType('CommunityDict', dict[CommunityName, tuple[CourseId | None, SubcommunityDict]])
Username = NewType('Username', str)

# Type aliases for better readability
# SubcommunitiesDict = dict[SubcommunityName, CourseId]
# EducationTypesList = list[EducationType]
AdminUsersList = list[Username]

# Union types for flexibility
CommunityIdentifier = CommunityName | CourseId


# noinspection PyClassHasNoInit
@define
class CanvasConfig:
    """"
    save the urls and API_key in a safe space using
    keyring (works on macOS and Windows)"""
    namespace = "canvasrobot"
    gui_root: object = None
    reset_api_keys: bool = False
    url: str = ""
    api_key: str = ""
    admin_id: int = 0
    api_fields = (
        dict(msg="Enter your Canvas URL (like https://[name].instructure.com)",
             key="url"),
        dict(msg="Enter your Canvas APi Key",
             key="api_key"),
        dict(msg="Enter your Canvas Admin id or 0 ",
             key="admin_id"),
    )

    # start_month = 8

    def __attrs_post_init__(self):
        if self.reset_api_keys:
            self.reset_keys()
        self.get_values()

    def get_values(self):
        """ ask for canvas url, api key and admin_id, uses keyring to
        store them in a safe space"""

        for field in self.api_fields:
            value = self.get_value(field["msg"], field["key"])
            self.__setattr__(field["key"], value)

    def get_value(self, msg, entry):
        """get value for entry from keychain if present
           else ask the user to supply value (and store it)"""
        value = keyring.get_password(self.namespace, entry)
        if value in (None, ""):
            # noinspection PyTypeChecker
            value = simpledialog.askstring("Input",
                                           msg,
                                           parent=self.gui_root) \
                if self.gui_root else Prompt.ask(msg)
            keyring.set_password(self.namespace, entry, value)
            value = keyring.get_password(self.namespace, entry)
        return value

    def reset_keys(self):
        for field in self.api_fields:
            # noinspection PyUnresolvedReferences
            try:
                keyring.delete_password(self.namespace, field['key'])
            except keyring.errors.PasswordDeleteError:
                logging.info(f"key '{field['key']}' not found in "
                             f"'{self.namespace}' keyring storage")
                pass


# School specific
EDUCATIONS = ('BANL',
              'BAUK',
              'MA',
              'PM_MA',
              'ULO',
              'PM_ULO',
              'MACS',
              'PM_MACS',
              'GV',
              'PM_GV',
              'BIJVAK'
              )


# the 'communities-courses' which can have subcommunities/edu_label(to retrieve students from Dibsa)


subcies_ba_nl = SubcommunityDict({
    SubcommunityName("banl"): (None, CourseLanguage('nl')),
    SubcommunityName("pm_ma"): (None, CourseLanguage('nl')),
    SubcommunityName("pm_ulo"): (None, CourseLanguage('nl')),
    SubcommunityName("pm_gv"): (None, CourseLanguage('nl'))
})

subcies_ba_uk = SubcommunityDict({
    SubcommunityName('bauk'): (None, CourseLanguage('uk')),
    SubcommunityName('pm_macs'): (None, CourseLanguage('uk'))
})

subcies_ma_nl = SubcommunityDict({
    SubcommunityName("ma"): (None, CourseLanguage('nl')),
    SubcommunityName("gv"): (CourseId(16066), CourseLanguage('nl')),  # unpublished
    SubcommunityName("ulo"): (CourseId(4229), CourseLanguage('nl'))  # unpublished
})

subcies_ma_all = SubcommunityDict({
    SubcommunityName("ma"): (None, CourseLanguage('nl')),
    SubcommunityName("gv"): (CourseId(16066), CourseLanguage('nl')),  # unpublished
    SubcommunityName("ulo"): (CourseId(4229), CourseLanguage('nl')),  # unpublished
    SubcommunityName("macs"): (CourseId(4230), CourseLanguage('uk'))  # unpublished
})


# id, dict of subcommunities
COMMUNITIES = CommunityDict({
    CommunityName("tststudent"): (CourseId(21329), subcies_ba_nl | subcies_ba_uk |
                                  subcies_ma_all),  # v
    CommunityName("acskills"): (CourseId(4485), subcies_ba_nl | subcies_ba_uk | subcies_ma_nl),  # v
    CommunityName("macs"): (CourseId(4230), None),  # v
    CommunityName("all_banl"): (CourseId(4221), subcies_ba_nl),  # v
    CommunityName("all_bauk"): (CourseId(4227), subcies_ba_uk),  # v
    CommunityName("all_ma"): (CourseId(4228), subcies_ma_nl)  # v
})


SHORTNAMES = dict(
    bho1=4285,
    bho2=4440,
    bho3=4441,
    bgo1=10540,
    theol_credo=4472,
    # theoonline=4472, None),
    spirsam=7660)

STUDADMIN = ('rsackman',
             'smvries')

ENROLLMENT_TYPES = dict(student='StudentEnrollment',
                        teacher='TeacherEnrollment',
                        observer='ObserverEnrollment',
                        teachingassistant='TeachingAssistantEnrollment')


@define
class Community:
    """
    Represents a Canvas LMS community with its associated subcommunities.

    A community can have:
    - A main courseID
    - Optional subcommunities (each with their own course ID)
    - Associated education types
    - Metadata about the community
    """

    # Core identification
    name: CommunityName
    course_id: CourseId

    # Optional subcommunities - maps subcommunity name to course ID
    subcommunities: Optional[SubcommunityDict] = None

    # Metadata
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    # Administrative info
    admin_users: AdminUsersList = []

    def __post_init__(self):
        """Ensure subcommunities is a dict if provided"""
        if self.subcommunities is None:
            self.subcommunities = SubcommunityDict({})

    @property
    def has_subcommunities(self) -> bool:
        """Check if this community has any subcommunities"""
        return bool(self.subcommunities)

    @property
    def subcommunity_course_ids(self) -> list[int]:
        """Get all course IDs from subcommunities"""
        course_ids = []
        if self.subcommunities:
            course_ids.extend(self.subcommunities.values())
        return course_ids

    @property
    def all_course_ids(self) -> list[int]:
        """Get all course IDs including the main course and subcommunities"""
        course_ids = [self.course_id]
        if self.subcommunities:
            course_ids.extend(self.subcommunities.values())
        return course_ids

    @property
    def subcommunity_names(self) -> list[SubcommunityName]:
        """Get all edu_labels in the subcommunities"""
        if self.subcommunities is None:
            return []
        keys = self.subcommunities.keys()
        return [SubcommunityName(key) for key in keys]

    def get_subcommunity_course_id(self, subcommunity_name: SubcommunityName) -> CourseId:
        """Get course ID for a specific subcommunity"""
        return self.subcommunities.get(subcommunity_name)[0] if self.subcommunities else None

    def get_subcommunity_language(self, subcommunity_name: SubcommunityName) -> CourseLanguage:
        """Get course ID for a specific subcommunity"""
        return self.subcommunities.get(subcommunity_name)[1] if self.subcommunities else None

    def add_subcommunity(self, name: SubcommunityName, course_id: CourseId, language: CourseLanguage) -> None:
        """Add a new subcommunity"""
        if self.subcommunities is None:
            self.subcommunities = SubcommunityDict({})
        self.subcommunities[name] = course_id, language

    @classmethod
    def from_legacy_data(cls, name: str, legacy_data: tuple) -> 'Community':
        """
        Create a Community instance from the existing COMMUNITIES dictionary format.

        Args:
            name: Community name (key from COMMUNITIES dict)
            legacy_data: Tuple of (course_id, subcommunities_dict_or_none)
            # data = tuple(course_id, {subcommunity_name:(id, "nl"|"uk")} )

                    """
        course_id, subcommunities = legacy_data

        return cls(
            name=CommunityName(name),
            course_id=CourseId(course_id),
            subcommunities=subcommunities,
        )


@define
class CommunityManager:
    """
    Manages a collection of communities and provides utility methods.
    """
    communities: dict[CommunityName, Community] = {}

    def __attrs_post_init__(self):
        """Ensure communities is a dict"""
        if not isinstance(self.communities, dict):
            object.__setattr__(self, 'communities', {})

    @property
    def community_names(self) -> list[str]:
        """ get a list of (top)community names"""
        return list(self.communities.keys())

    @property
    def community_course_ids(self) -> set[str]:
        """
        Get a list of all subcommunity names across all communities
        """
        course_ids = set()
        for community in self.communities.values():
            course_ids.add(community.course_id)
        return course_ids

    @property
    def subcommunity_names(self) -> set[str]:
        """
        Get a list of all subcommunity names across all communities
        """
        sc_names = set()
        for community in self.communities.values():
            new_names = community.subcommunity_names
            sc_names.update(new_names)
        return sc_names

    def add_community(self, community: Community) -> None:
        """Add a community to the manager"""
        self.communities[community.name] = community

    def get_community(self, name: CommunityName) -> Optional[Community]:
        """Get a community by name"""
        return self.communities.get(name)

    def get_course_id_by_name(self, name: CommunityName | SubcommunityName) -> CourseId | None:
        """Find a (sub)community by its (short)name and return course_id or return None if not found."""
        found = self.communities.get(name)
        if found:
            return found.course_id
        # Find a subcommunity course ID
        for community in self.communities.values():
            course_id = community.get_subcommunity_course_id(name)
            return course_id
        else:
            return None

    def get_community_by_name(self, name: CommunityName) -> Community | None:
        """Find a community by its (short)name or return None if not found."""
        found = self.communities.get(name)
        return found

    def get_community_by_course_id(self, course_id: CourseId) -> Community | None:
        """Find a community by its course_id or return None if not found."""
        for community in self.communities.values():
            if community.course_id == course_id:
                return community
        else:
            return None

    def get_subcommunity_by_course_id(self, course_id: int) -> Optional[Community]:
        """Find a community by its main course ID or subcommunity course ID"""
        for community in self.communities.values():
            if course_id in community.all_course_ids:
                return community
        return None

    def get_edulabels_by_course_id(self, course_id: CourseId) -> list[str]:
        """Get a list of subcommunity_names/edulabels for a given CourseId"""
        community = self.get_community_by_course_id(course_id)
        if community:
            return community.subcommunity_names or [community.name]
        return []

    @classmethod
    def from_legacy_communities(cls, communities_dict: dict[CommunityName,
                                tuple[CourseId,
                                      dict[SubcommunityName, tuple[CourseId, CourseLanguage]]]]) -> 'CommunityManager':
        """
        Create a CommunityManager from the existing COMMUNITIES dictionary.

        Args:
            communities_dict: The existing COMMUNITIES dictionary
        """
        manager = cls()
        for name, data in communities_dict.items():
            # name = community_name
            # data = (course_id, {subcommunity_name: (id,"nl"|"uk")} )
            community = Community.from_legacy_data(name, data)
            manager.add_community(community)
        return manager


now = datetime.now()
# July first is considered the end of the educational season
AC_YEAR = now.year - 1 if now.month < 8 else now.year
LAST_YEAR = '-{0}-{1}'.format(AC_YEAR - 1, AC_YEAR)
THIS_YEAR = '-{0}-{1}'.format(AC_YEAR, AC_YEAR + 1)
NEXT_YEAR = '-{0}-{1}'.format(AC_YEAR + 1, AC_YEAR + 2)

EXAMINATION_FOLDER = "Tentamens"


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
    def __init__(self, is_testing=False, fake_migrate_all=False, folder="databases"):
        url = 'sqlite://testing.sqlite' if is_testing else 'sqlite://storage.sqlite'
        super(LocalDAL, self).__init__(url,
                                       folder=folder,
                                       migrate=True,
                                       migrate_enabled=True,
                                       fake_migrate=False,
                                       fake_migrate_all=fake_migrate_all)

        self.define_table('setting',
                          Field('last_db_update', 'datetime'),
                          singular='Canvasrobot setting',
                          plural='CanvasRobot settings',
                          migrate=False)

        self.define_table('course',
                          Field('course_id', 'integer'),
                          Field('course_code', 'string'),
                          Field('sis_code', 'string'),
                          Field('account_id', 'integer'),
                          Field('term', 'string'),
                          Field('ac_year', 'string'),
                          Field('name', 'string'),
                          Field('creation_date', 'date'),
                          Field('teachers', 'list:string'),  # as usernames
                          Field('teachers_names', 'list:string'),
                          Field('status', 'integer'),
                          Field('nr_students', 'integer'),
                          Field('nr_modules', 'integer'),
                          Field('nr_module_items', 'integer'),
                          Field('nr_pages', 'integer'),
                          Field('nr_assignments', 'integer'),
                          Field('nr_quizzes', 'integer'),
                          Field('nr_files', 'integer'),
                          # Field('nr_collaborations', 'integer'),
                          Field('nr_ext_urls', 'integer'),
                          Field('assignments_summary', 'string'),
                          Field('examinations_summary', 'string'),
                          Field('examinations_ok', 'boolean', default=False),
                          Field('examinations_findings', 'string'),
                          Field('examinations_details_osiris', 'string'),
                          Field('gradebook', 'upload', uploadfield='gradebook_file'),
                          Field('gradebook_file', 'blob'),
                          singular='LMS course',
                          plural='LMS courses',
                          format='%(name)s[%(teacher_names)s]')

        # To record a controlled set of names referring to examination assignments.
        # We override the (sound) pyDAL principle to use course->id as reference
        # because we need the canvas course_id for browser links
        # Note that Pydal create a foreign key to course->id we need to change
        # using DBrowser
        self.define_table('examination',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'id',
                                                             self.course._format)),
                          Field('course_name', 'string'),  # a bit redundant
                          Field('name', 'string'),
                          Field('ignore', 'boolean',
                                label="Skip unused/unusable assignments",
                                default=False),
                          format='%(name)s',
                          singular='Examination name',
                          plural='Examination names')

        self.define_table('user',
                          Field('user_id', 'integer'),
                          Field('username', 'string'),
                          Field('fname', 'string'),
                          Field('first_name', 'string'),
                          Field('prefix', 'string'),
                          Field('last_name', 'string'),
                          Field('email', 'string'),
                          Field('primary_role', 'string', requires=valid_roles),
                          format=('%(first_name)s %(prefix)s '
                                  '%(last_name)s[%(username)s]'),
                          singular='User',
                          plural='Users')

        self.define_table('course2user',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'course.id',
                                                             self.course._format)),
                          Field('user',
                                'reference user',
                                requires=validators.IS_IN_DB(self, 'user.id',
                                                             self.user._format)),
                          Field('role', 'string',
                                requires=valid_roles))

        # self.course.no_students = Field.Virtual(
        #   'no_students',
        #   lambda row: self.((self.course2user.course == row.course.id) &
        #                     (self.course2user.role == 'S')).count())

        self.define_table('submission',
                          Field('submission_id', 'integer'),
                          Field('assigment_id', 'integer'),
                          Field('course_id', 'integer'),
                          Field('user_id', 'integer'),
                          Field('submission_type', 'string'),
                          Field('url', 'string'),
                          Field('grade', 'string'),
                          Field('graded_at', 'string'),
                          format='%(submission_id)s-%(assigment_id)s %(user_id)s',
                          singular='Submission',
                          plural='Submissions')

        self.define_table('document',
                          Field('course',
                                'reference course',
                                requires=validators.IS_IN_DB(self, 'course.id',
                                                             self.course._format)),
                          Field('filename', 'string'),  # from lms
                          Field('content_type', 'string'),  # from lms
                          Field('size', 'integer'),  # from lms
                          Field('folder_id', 'integer'),  # from lms
                          Field('url', 'string'),  # from lms
                          # editor 0= unchecked 1= failed =  2: ok
                          Field('check_status', 'integer', default=0),
                          Field('upload_status', 'integer'),  # upload status lms
                          Field('download_status', 'integer'),  # upload status lms
                          Field('memo', 'string'),  # memo
                          # safe upload of files, keeps filenames
                          Field('file', 'upload'),
                          migrate=True)

        self.define_table('course_urltransform',
                          Field('dryrun', 'boolean'),
                          Field('course_id', 'integer'),
                          Field('course_code', 'string'),
                          Field('account_id', 'integer'),
                          Field('term', 'string'),
                          Field('name', 'string'),
                          Field('teacher_logins', 'list:string'),  # as usernames
                          Field('teacher_names', 'list:string'),
                          Field('teacher_emails', 'list:string'),
                          Field('status', 'integer'),
                          Field('nr_pages', 'integer'),
                          Field('nr_module_items', 'integer'),
                          Field('nr_assignments', 'integer'),
                          Field('nr_quizzes', 'integer'),
                          Field('nr_files', 'integer'),
                          Field('titles', 'list:string'),
                          Field('urls', 'list:string'),
                          Field('module_items', 'list:integer'),
                          Field('html_report', 'text'),
                          singular='Course Url transform',
                          plural='Course Url transforms',
                          format='%(name)s[%(teacher_names)s]')

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

# Create from existing data
community_manager = CommunityManager.from_legacy_communities(COMMUNITIES)
