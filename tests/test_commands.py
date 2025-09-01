from click.testing import CliRunner
from canvasrobot.commandline import cli


def test_enroll_student():
    # werkt jan 2025
    runner = CliRunner()
    # t = type(cli)
    # t = is <class 'rich_click.rich_command.RichCommand'>
    # next line generates warning on 'cli' arg 'Expected type 'BaseCommand' but it is 'Any'
    # https://stackoverflow.com/questions/77845322/unexpected-warning-in-click-cli-development-with-python
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['enroll', 'student'],
                           input='ndegroot\ntheol_credo')
    assert result.exit_code == 0
    assert 'ndegroot is toegevoegd ' in result.output
    assert '4472' in result.output
    # repair the live canvas environment
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['enroll', 'student', '--unenroll'],
                           input='ndegroot\ntheol_credo')
    assert 'is verwijderd als student' in result.output


def test_search_course():
    # works: 23 jan 2025
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['search', 'in-course'],
                           input='zoek\njezelf\n34\n')
    assert result.exit_code == 0
    assert "1 locations" in result.output


def test_search_course_for_mediasite():
    # works?
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['search', 'in-course'],
                           input='zoek\nmediasite\n34\n')
    assert result.exit_code == 0
    assert "5 locations in 1 page" in result.output


def test_search_all_courses():
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['search', 'in-courses'],
                           input='zoek\njezelf\n')
    assert result.exit_code == 0
    assert '10 locations in 9 pages' in result.output


def tst_db_auto_update_no_value():
    # no arg : False (default)
    # arg no value: True
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli,
                           ['--db_auto_update'])
    assert not result

