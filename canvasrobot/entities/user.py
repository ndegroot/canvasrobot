import collections
import re
import canvasapi

class User:
    """Can be initialized with a canvasapi.user.User, a dict or with args & values"""
    def __init__(self,
                 *args, **varg) -> None:
        if args and isinstance(args[0], canvasapi.user.User):
            self.user_id = args[0].id
            self.name = args[0].name
        elif len(args) > 1:
            self.user_id,  # lms user_id
            self.username,
            self.name,
            self.first_name,
            self.prefix,
            self.last_name,
            self.email = args
        elif type(varg) == dict:
            self.__dict__ = varg

    # noinspection PyAttributeOutsideInit
    def parse_sortable_name(self, sortable_name):
        """examples:
        Klein, Wim
        Groot, Nico de
        Goyvaert, Samuel (Sam)
        Wieringen, Archibald (H.M.J.)
        set the fields: first_name, prefix, last_name
        """

        assert ", " in sortable_name, "sortable_name should contain comma"
        source = sortable_name
        pat = re.compile(
            r'(?P<last_name>[\w \-]+), (?P<first_name>\w+)\s?((\((?P<first_name_par>\w+)\))|'
            r'(\((?P<init>[\w.]+.)\)))?(\s*(?P<prefix>\w+))?')
        d = re.match(pat, source)
        if not d:
            raise Exception("sortable_name failed parsing")

        self.first_name, self.prefix, self.last_name = (d['first_name_par'] or
                                                        d['first_name'], d['prefix'] or
                                                        '', d['last_name'])




# UserDTO = collections.namedtuple('UserDTO', 'user_id')
# for now we can use User
EnrollDTO = collections.namedtuple('EnrollDTO', 'user_id username course_id course role')

# Enrollment = collections.namedtuple('Enrollment', 'user')

# Profile = collections.namedtuple('Profile', 'login_id')

# Profile_ext = collections.namedtuple('Profile', 'id fname short_name sortable_name avatar_ur title bio primary_email '
#                                                'login_id integration_id time_zone locale effective_locale '
#                                                'calendar lti_user_id')
