# CanvasRobot
Library which uses
[Canvasapi](https://canvasapi.readthedocs.io/en/stable/getting-started.html)
(minimally patched to allow more flexible user search)
to provide a CanvasRobot class for GUI and commandline use.
You can install the commandline tools _canvasrobot_ and _urltransform_ (special edition 
to translate specific video urls in Canvas pages) 
using [UV](https://docs.astral.sh/uv/getting-started/installation/)

## Setup
Before installing the tools, you may need to download a package manager to install 
dependencies—pieces of code that the application relies on. On macOS, we will use 
_Homebrew_ and _UV_; on Windows, we will only use _UV_. Then, we will install the CanvasRobot tools.

To run the following prompts, one must copy and paste the commands in the command line 
and press the {enter} key after each line. During the setup, it might be necessary 
to restart the terminal after installing homebrew, uv, or transcribetools to 
be able to proceed. 

### Install UV
#### On Windows
1. Open Windows PowerShell or the Command shell. [How?](https://learn.microsoft.com/en-us/powershell/scripting/learn/ps101/01-getting-started?view=powershell-7.5)

2. Run prompt to install uv:

```bash
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### On macOS:
1. Open Terminal

2. Run prompt to install brew:

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

3. Run prompt to install uv:

```bash
brew install uv
```

### Install the tools
1. Install the (commandline) tools in this project.


```commandline
uv tool install canvasrobot

canvasrobot --help
urltransform --help
```

## Uses 
- [CanvasAPI](https://canvasapi.readthedocs.io/en/stable/getting-started.html) 
- rich (commandline output)
- rich_click (commandline input)
- keyring (safe store for the Canvas API key)
- pydal (to create a local SQLite database)
- pywebview (HTML reporting)
- [opt] pymemcache (install with `uv add pymemcache` to add caching the Canvas interaction, needs `memcached` installed)

## Used 
In `word2quiz` library.
(Not yet ready for general use...)

## Examples using the CanvasRobot class
```Python
import rich
import canvasrobot as cr

if __name__ == '__main__':

    console = rich.console.Console(width=160, force_terminal=True)

    robot = cr.CanvasRobot(reset_api_keys=False,
                           console=console)

    # robot.update_database_from_canvas()
    robot.create_folder_in_all_courses('Tentamens')

    # result = robot.enroll_in_course("", 4472, 'u752058',
    # 'StudentEnrollment') #  (enrollment={'type': 'StudentEnrollment'}
    
    # user = robot.search_user('u752058')
    # print(user)
    # if not user:
    #   print(robot.errors)

    #COURSE_ID = 9999  # test course
    #result = robot.create_folder_in_course_files(COURSE_ID, 'Tentamens')

    # print(robot.course_metada(COURSE_ID))
    # print(robot.unpublish_folderitems_in_course(COURSE_ID,
    #                                            foldername,
    #                                            files_too=True))

    #course = robot.get_course(COURSE_ID)
    # tab = robot.get_course_tab_by_label(COURSE_ID, "Files")
    # print(tab.visibility)

    # for course_id in (COURSE_ID, COURSE_ID2):
    #     result = robot.create_folder_in_course_files(course_id, 'Tentamens')

    # result = robot.unpublish_subfolder_in_all_courses(foldername,
    #                                                  files_too=True,
    #                                                  check_only=True)
    # if course_ids_missing_folder:
    #    logging.info(f"Courses with missing folder {foldername}: {course_ids_missing_folder}")

    # QUIZZES -----------------------------
    # filename = 'Q_A.docx'
    # robot.create_quizzes_from_document(filename=filename,
    #                                    course_id=COURSE_ID,
    #                                    question_format='Vraag {}. Vertaal:',
    #                                    adjust_fontsize=True,
    #                                    testrun=False
    #                                    )
```

[![PyPI version](https://badge.fury.io/py/canvasrobot.svg)]
