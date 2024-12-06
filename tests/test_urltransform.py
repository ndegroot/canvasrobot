import pytest
import textwrap


def test_mediasite2panopto(tr):
    """
    :param tr: fixture: the TransformationRobot based on CanvasRobot
    :returns: True if url is transformed and 'bad' url is not transformed and reported
    """

    source = textwrap.dedent("""\
    replace the ms_id with p_id in the

    https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731d]

    Nu een link met id die niet bestaat https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731 
    is dus niet goed 

    replace by (redirect procedure until dec 2024)


    """)
    target, updated = tr.mediasite2panopto(source)
    print(target)

    assert updated, "'updated' should be 'True' as 'source' contains a videocollege url"
    assert ('https://tilburguniversity.cloud.panopto.eu/Panopto/'
            'Pages/Viewer.aspx?id=221a5d47-84ea-44e1-b826-af52017be85c') in target
    # don't change non-redirecting urls, report them
    bad_ms_url = 'https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731'
    assert bad_ms_url in target, f"{bad_ms_url} should not be changed"

    assert bad_ms_url in tr.transformation_report
