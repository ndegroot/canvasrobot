import bs4
# from pydal.objects import Row, Rows
import textwrap
from click.testing import CliRunner
from canvasrobot.urltransform import cli
from canvasrobot.urltransform import Transformation
# from canvasrobot import UrlTransformationRobot
from main import TEST_COURSE
from conftest import page_html
from bs4 import BeautifulSoup, NavigableString


def test_scan_all_cli():
    """ cli calls  """
    admin_id: int = 0  # 20  # 6  #20

    # CliRunner uses the regular db
    runner = CliRunner()
    # opt-out needed for type of parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '-a', '--admin_id', admin_id])  # dryrun = True, default
    assert result.exit_code == 0
    # assert bad_ms_url not in result.output
    # assert 'Mediasite_id ce152c1602144b80bad5a222b7d4cc731 not found' in result.output


def test_scan_all_cli_20():
    """ cli calls  """
    admin_id: int = 20  # 6  #20

    # CliRunner uses the regular db
    runner = CliRunner()
    # opt-out needed for type of parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '-a', '--admin_id', admin_id])  # dryrun = True, default
    assert result.exit_code == 0
    # assert bad_ms_url not in result.output
    # assert 'Mediasite_id ce152c1602144b80bad5a222b7d4cc731 not found' in result.output


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
    """TransformedPage is used to collect data about the transformed pages"""

    _ = Transformation(title="eerste", url="https://example1.com")
    _ = Transformation(title="tweede", url="https://example2.com")

    assert Transformation.get_column('title') == ["eerste",
                                                  "tweede"]
    assert Transformation.get_column('url') == ["https://example1.com",
                                                "https://example2.com"]


def test_transform_urls_single(tr):
    # `tr` is the pytest fixture- td.db is the test database
    testcourse_id: int = TEST_COURSE
    tr.transform_urls_in_course(testcourse_id, dryrun=True)
    transform_data = tr.get_transform_data(testcourse_id)
    assert transform_data, f"Make sure course {testcourse_id} contains transform candidates"


def test_scan_single_cli():
    """ cli calls  """
    testcourse_id: int = TEST_COURSE

    # CliRunner uses the regular db
    runner = CliRunner()
    # opt-out needed for type of parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '-s', testcourse_id,])  # dryrun = True, default
    assert result.exit_code == 0
    # assert bad_ms_url not in result.output
    # assert 'Mediasite_id ce152c1602144b80bad5a222b7d4cc731 not found' in result.output


def test_scan_single_cli_lc_dutch():
    testcourse_id: int = 17236  # LC cursus Dutch
    # CliRunner uses the regular db
    # calls
    runner = CliRunner()
    # opt-out needed for type of parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '-s', testcourse_id,])  # dryrun = True, default
    assert result.exit_code == 0
    assert 'Transformations completed' in result.output, "Expected confirmation of completed transformations"


def test_transform_single_cli_sam():
    testcourse_id: int = 16627
    # CliRunner uses the regular db
    runner = CliRunner()
    # opt-out needed for type of parameter 'cli': see https://youtrack.jetbrains.com/issue/PY-66428
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '-s', testcourse_id,])  # dryrun = True, default
    assert result.exit_code == 0
    assert 'Transformations completed' in result.output, "Expected confirmation of completed transformations"


def test_transform_export_course():
    """test export to XLS file on base of db.courses.urltransform"""
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['export', '--single_course', 34])  # dryrun = True, default
    assert result.exit_code == 0
    assert 'Excel-bestand gegenereerd: output.xlsx' in result.output
    assert 'no errors recorded' in result.output


def test_transform_export_courses():
    """test export to XLS file on base of db.courses.urltransform all courses
    calls export_courses_to_excel"""
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['export', '--all_courses'])
    assert result.exit_code == 0
    assert 'Excel-bestand gegenereerd: output.xlsx' in result.output
    assert 'no errors recorded' in result.output


def test_transform_export_courses_admin():
    """test export to XLS file on base of db.courses.urltransform all courses"""
    admin_id = 20
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['export', '--all_courses', '--admin_id', admin_id])
    assert result.exit_code == 0
    assert 'Excel-bestand gegenereerd: output.xlsx' in result.output
    assert 'no errors recorded' in result.output


def test_transform_export_courses_missing_param():
    """test export to XLS file on base of db.courses.urltransform"""
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['export', '--all_courses'])  # dryrun = True, default
    assert result.exit_code == 0
    assert 'Excel-bestand gegenereerd: output.xlsx' in result.output
    assert 'no errors recorded' in result.output


def test_transform_all():
    runner = CliRunner()
    # noinspection PyTypeChecker
    result = runner.invoke(cli, ['scan', '--all_courses'])

    assert result.exit_code == 0
    # assert bad_ms_url not in result.output


def tst_parsing():

    def has_ns_string(ele: bs4.PageElement):
        """:returns True is ele has string leafs"""
        if isinstance(ele, bs4.NavigableString):
            # can't have children
            return False
        for child in ele.children:
            if isinstance(child, bs4.NavigableString):
                return True
        else:
            return False

    def has_child_nodes(ele: bs4.PageElement):
        """:returns True is ele has child nodes
           if child is a NavigableString or br-tag it's NOT considered a child
        """

        for child in ele.children:
            # we need an extra check NS of tag br is *not* a real child
            if not isinstance(child, NavigableString) and child.name != 'br':
                # must be a node, right?
                return True
        else:
            return False
    soup = BeautifulSoup(page_html, 'lxml')
    items = list(soup.descendants)
    top_nodes = (0, 1)  # top nodes, tags html, body
    # actions: ignore
    # ignore = (5, 7, 27, 23, 27)
    # a candidate has one or more leafs (NavString) to process, and nodes elements. Can be: span, a, iframe
    # 3 has NS and br
    # 6 has NS and a span with a (=9)
    # 11 is an a, has 3 NS
    # 15 is div, has 2 NS
    # 18 is p, no NS, has iframe=19
    # 19 is iframe
    # 24 div has NS, span=25
    # 25 span has NS,span=28
    # 28 span has NS, a=30
    # 30 a with NS
    # 37 span met NS link-as-text
    # 43 span met NS
    nodes = (2, 3, 5, 6, 7, 9, 15, 18, 21, 24, 25, 27, 28, 32, 34, 35, 37, 39, 41, 43, 45, 46)  # span, div, p, br
    # It might contain node or leafs, we will handle them later
    # actions: none
    link_nodes = (11, 19, 30)  # a, iframe
    # leaf, has href or src and possibly NS
    # actions: process src/href (ns wil come up later)
    navstring_leaf = (8, 10, 12, 13, 14, 16, 17, 20, 22, 23, 26, 29, 31, 33, 36, 38, 40, 42, 44)  # leafs
    # actions: process
    for ndx, item in enumerate(items, start=0):
        if ndx in top_nodes:
            assert has_child_nodes(item), f"has_child_node failed on item_no {ndx} {item.name}"
        if ndx in nodes:
            assert item.name in ('span', 'div', 'p', 'br')
            # assert has_child_nodes(item), f"Candidates has_child_nodes failed on item_no {ndx} {item.name}"
        if ndx in link_nodes:
            assert item.name in ('a', 'iframe'), f" not a link_leaf {ndx} {item.name}"
            # assert not has_child_nodes(item), f"link_leafs has_child_nodes failed on item_no {ndx} {item.name}"
        if ndx in navstring_leaf:
            assert isinstance(item, NavigableString)  # sufficient
            assert "children" not in item
            assert not has_ns_string(item)
