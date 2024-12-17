from result import is_ok, is_err, Result
import rich
from rich.prompt import Prompt
import rich_click as click

from .commandline_model import (get_logger,
                                CanvasRobot,
                                create_db_folder,
                                enroll_student,
                                search_in_course,
                                search_in_courses,
                                search_replace_pages,
                                search_replace_show,
                                show_search_result,
                                overview_courses,
                                overview_documents,
                                )


@click.group(no_args_is_help=True,
             epilog='Check out our docs at https://github.com/ndegroot/canvasrobot for more details')
@click.version_option(package_name='canvasrobot')
@click.pass_context  # our 'global' context
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
def cli(ctx: click.Context, reset_api_keys, db_auto_update, db_force_update):
    """main entry point for commandline"""
    click.echo("create db folder if needed")
    path = create_db_folder()

    click.echo("create Canvasrobot")
    robot = CanvasRobot(reset_api_keys=reset_api_keys,
                        db_auto_update=db_auto_update,
                        db_force_update=db_force_update,
                        db_folder=path)

    ctx.obj = robot


@cli.command()
def sync():
    click.echo("syncing ready")


# define multi commands/groups
@cli.group("enroll")
def enroll():
    pass


@cli.group("search")
def search():
    pass

# @cli.group("get")
# def get():
#     pass


@cli.group("show")
def show():
    pass


@click.command("student")
@click.pass_obj
def student(robot):
    enroll_student(robot)


@click.command("enroll_students_in_communities")
@click.pass_obj
def students_in_communities(robot):
    """enroll current students in the educational communities"""
    robot.enroll_students_in_communities


@click.command()
@click.pass_obj
def in_course(robot):
    search_in_course(robot)


@click.command()
@click.pass_obj
def in_courses(robot):
    search_in_courses(robot)
    # overview_courses(courses, robot.canvas_url)


@click.command()
@click.pass_obj
def courses(robot):
    courses = robot.get_courses_in_account()
    overview_courses(courses, robot.canvas_url)


@click.command()
@click.pass_obj
@click.option("--course_id",
              default=None,
              help="course_id to show documents for")
def documents(robot, course_id: int = None):
    documents = robot.get_list_of_documents_db(course_id=course_id)
    overview_documents(documents, robot.canvas_url)


# connect commands to each subcommand
enroll.add_command(student)
enroll.add_command(students_in_communities)

search.add_command(in_course)
search.add_command(in_courses)

# get.add_command(get)

show.add_command(courses)
show.add_command(documents)


if __name__ == '__main__':
    cli()
    # console = rich.console.Console(width=120, force_terminal=True)
