import canvasapi


class Guest:
    def __init__(self,
                 *args, **varg) -> None:
        if args and isinstance(args[0], canvasapi.user.User):
            self.user_id = args[0].id
            self.name = args[0].name
        elif len(args) > 1:
            self.user_id,  # lms user_id
            self.guest_id,  # needed?
            self.username,  # TiU username
            self.anr,
            self.name,
            self.organisation,
            self.start_date,
            self.end_date,
            self.group_id,
            self.status,
            self.memo = args
        elif type(varg) == dict:
            self.__dict__ = varg

