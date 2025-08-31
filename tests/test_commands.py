from click.testing import CliRunner
from canvasrobot.commandline import cli


def test_enroll_student():
    runner = CliRunner()
    # t = type(cli)
    # t = is <class 'rich_click.rich_command.RichCommand'>
    # next line generates warning on 'cli' arg 'Expected type 'BaseCommand' but it is 'Any'
    # https://stackoverflow.com/questions/77845322/unexpected-warning-in-click-cli-development-with-python
    result = runner.invoke(cli,
                           ['--do', 'enroll_student'],
                           input='ndegroot\ntheol_credo')
    assert result.exit_code == 0
    assert 'Nico de Groot' in result.output
    assert '4472' in result.output


def test_search_course():
    runner = CliRunner()
    result = runner.invoke(cli,
                           ['--do', 'search_course'],
                           input='zoek\njezelf\n34\n')
    assert result.exit_code == 0


def test_search_all_courses():
    runner = CliRunner()
    result = runner.invoke(cli,
                           ['--do', 'search_all'],
                           input='zoek\njezelf\n')
    assert result.exit_code == 0
    assert 'Nico de Groot' in result.output


def tst_db_auto_update_no_value():
    # no arg : False (default)
    # arg no value: True
    runner = CliRunner()
    result = runner.invoke(cli,
                           ['--db_auto_update'])
    assert not result



