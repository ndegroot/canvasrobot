import os
import sys
# import keyring
import pytest
import configparser
import getpass
import pathlib

import urllib3.connectionpool

from canvasrobot import CanvasRobot
from urltransform import UrlTransformationRobot

# from pymemcache.client import base
page_html = """<div><span>Pagina om de vervanging te testen van Mediasite URLs door de vervangende Panopto URLs. 
Dat gaat tot 3 februari 2025 via de redirect server.<br /></span><span><br />
Kandidaat voor vervanging in een link: <span> 
<a href="https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731d">link mediasite</a> </span></span></div>
<div>Kandidaat in iframe</div>
<p><iframe title="TheOnline-Preambule 2" 
src="https://videocollege.uvt.nl/Mediasite/Play/009e033f47cc4330ba2e4c3a0deecd461d" 
width="900" height="600" allowfullscreen="allowfullscreen" allow="fullscreen"></iframe></p>
<p>&nbsp;</p>
<div><span>Link met URL die niet vervangen hoeft te worden:<br /><span>
<a href="https://tilburguniversity.cloud.panopto.eu/Panopto/Pages/Viewer.aspx?id=221a5d47-84ea-44e1-b826-af52017be85c">
panoptolink</a><br /></span> <span><br /></span> 
<span>Nu een link met id die niet bestaat in de datatabel:<br />
https://videocollege.uvt.nl/Mediasite/Play/ce152c1602144b80bad5a222b7d4cc731 <br />
</span><span>Dat is dus niet goed, zou gerapporteerd moeten worden.</span><span><br /></span></span></div>"""


def dropdb(thedb):
    for table_name in thedb.tables():
        thedb[table_name].drop()
    thedb.commit()


@pytest.fixture(scope='session')
def cr():
    """ Fixture to set up the canvasrobot """
    try:
        cr = CanvasRobot(is_testing=True)
    except urllib3.connectionpool.MaxRetryError:
        print("No connection made to CanvasRobot.")
    # do something to initialise
    # localDAL handles truncate of the tables if is_testing
    else:
        yield cr
    # do something to teardown


@pytest.fixture(scope='session')
def tr():
    """ Fixture to set up the UrlTranformationRobot"""
    try:
        # while testing we use the 'databases' folder in the root of project
        db_folder = pathlib.Path.cwd().parent / "databases"
        tr = UrlTransformationRobot(is_testing=True,
                                    db_folder=db_folder)
    except urllib3.connectionpool.MaxRetryError:
        print("No connection")
    # do something to initialise
    # localDAL handles truncate of the tables if is_testing
    else:
        yield tr
    # do something to teardown


@pytest.fixture(scope='session')
def suspend_capture(pytestconfig):
    class suspend_guard:
        def __init__(self):
            self.capmanager = pytestconfig.pluginmanager.getplugin('capturemanager')

        def __enter__(self):
            self.capmanager.suspend_global_capture(in_=True)

        def __exit__(self, _1, _2, _3):
            self.capmanager.resume_global_capture()

    yield suspend_guard()


@pytest.fixture(scope='session')
def user_input(request):
    """ Asks user to check something manually and answer a question
    """

    def _user_input(msg='', hide_pw=False):
        notification = "\n\n<<\tANSWER NEEDED\t>>\n\n{}:".format(msg)

        # suspend input capture by py.test so user input can be recorded here
        capture_manager = request.config.pluginmanager.getplugin('capturemanager')
        capture_manager.suspend_global_capture(in_=True)

        answer = getpass.getpass(prompt=notification) if hide_pw \
            else input(notification)

        # resume capture after question have been asked
        capture_manager.resume_global_capture()

        # logging.debug("Answer: {}".format(answer))
        return answer

    # return the function that will be called by the test
    return _user_input


@pytest.fixture(scope='session')
def sso_config(suspend_capture):
    """
    create ini file if not already present and open it
    :return: parser object for ini file
    """
    dirs = os.path.split(__file__)[0]
    dirs.split(os.path.sep)[-2]

    sso_config = configparser.ConfigParser()
    home = str(pathlib.Path.home())
    path = os.path.join(home,
                        'sso_config.ini')
    if not os.path.exists(path):
        with suspend_capture:
            user_name = ask_user_input('accountname')
            user_passw = ask_password()
        sso_config['user'] = dict(name=user_name,
                                  password=user_passw)
        with open(path, "w") as config_file:  # NOTE don't use binary mode!
            sso_config.write(config_file)
    sso_config.read(path)
    sso_config.path = path  # monkey patch

    return sso_config


def get_platform():
    platforms = {
        'linux1': 'Linux',
        'linux2': 'Linux',
        'darwin': 'OS X',
        'win32': 'Windows'
    }
    if sys.platform not in platforms:
        return sys.platform

    return platforms[sys.platform]


def ask_user_input(msg=''):
    """ Asks user to check something manually and answer a question
    """
    notification = "\n\n>>>\tANSWER NEEDED\t<<<\n\n{}".format(msg)
    answer = input(notification)

    return answer


def ask_password(msg='Password'):
    """ Asks user to check something manually and answer a question
    """
    notification = "\n\n>>>\tANSWER NEEDED\t<<<\n\n{}".format(msg)
    answer = getpass.getpass(notification)

    return answer
