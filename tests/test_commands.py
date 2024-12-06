from click.testing import CliRunner
from commandline import run


def test_enroll_student():
    runner = CliRunner()
    # t = type(run)
    # t = is <class 'rich_click.rich_command.RichCommand'>
    # next line generates warning on 'run' arg 'Expected type 'BaseCommand' but it is 'Any'
    # https://stackoverflow.com/questions/77845322/unexpected-warning-in-click-cli-development-with-python
    result = runner.invoke(run,
                           ['--do', 'enroll_student'],
                           input='ndegroot\ntheol_credo')
    assert result.exit_code == 0
    assert 'Nico de Groot' in result.output
    assert '4472' in result.output


def test_search_all_courses():
    runner = CliRunner()
    result = runner.invoke(run,
                           ['--do', 'search_all'],
                           input='zoek\njezelf\n')
    assert result.exit_code == 0
    assert 'Nico de Groot' in result.output