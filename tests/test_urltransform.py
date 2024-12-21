from pydal.objects import Row, Rows
import textwrap
from click.testing import CliRunner
from canvasrobot.urltransform import cli
from canvasrobot.urltransform import TransformedPage
from main import TEST_COURSE


def test_mediasite2panopto(tr):
    """
    :param tr: fixture: the TransformationRobot based on CanvasRobot
    :returns: True if url is transformed and 'bad' url is not transformed and reported
    """

    source = textwrap.dedent("""\
    replace the ms_id with p_id in the

    <a href="https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731d">link mediasite</a>
    

    Nu een link met id die niet bestaat https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731 
    is dus niet goed 

    replace by (redirect procedure until dec 2024)


    """)
    target, updated, count_replacements = tr.mediasite2panopto(source, dryrun=False)
    print(target)

    assert updated, "'updated' should be 'True' as 'source' contains a videocollege url"
    assert count_replacements == 1, "should be 'True' as 'source' contains one old videocollege url"
    assert ('https://tilburguniversity.cloud.panopto.eu/Panopto/'
            'Pages/Viewer.aspx?id=221a5d47-84ea-44e1-b826-af52017be85c') in target
    # don't change non-redirecting urls, just report them
    bad_ms_url = 'https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731'
    assert bad_ms_url in target, f"{bad_ms_url} should not be changed"

    assert bad_ms_url in tr.transformation_report


def test_transformed_page():

    _ = TransformedPage(title="eerste", url="https://example1.com")
    _ = TransformedPage(title="tweede", url="https://example2.com")

    assert TransformedPage.get_column('title') == ["eerste",
                                                   "tweede"]
    assert TransformedPage.get_column('url') == ["https://example1.com",
                                                 "https://example2.com"]


def test_transform_single(tr):

    # tr is the pytest fixture- td.db is the test database
    testcourse_id: int = 34
    tr.transform_pages_in_course(testcourse_id, dryrun=True)
    transform_data = tr.get_transform_data(testcourse_id)
    assert transform_data, f"Make sure course {testcourse_id} contains transform candidates"


def test_transform_single_cli():
    testcourse_id: int = 34

    # CliRunner uses the regular db
    runner = CliRunner()
    # opt-out needed for parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['--single_course', testcourse_id,])  # dryrun
    assert result.exit_code == 0
    assert bad_ms_url not in result.output


def tst_transform_all():
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli)
    #                            ['--single_course', 34],

    assert result.exit_code == 0
    assert bad_ms_url not in result.output
