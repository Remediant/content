import base64

import demistomock as demisto  # noqa: F401
from CommonServerPython import *  # noqa: F401

WELCOME_MESSAGE = '''\n
# Welcome to XSOAR escape room
Here you will learn where all the magic happens.
But!
Before we start, you must prove you are a diamond in the rough.

Only the worthy shall pass.

Your first mission is finishing the playbook

'''


def main():
    data = base64.b64decode(FILE_CONTENT_BASE64)
    entry = fileResult('Test', data)
    entry.update({
        "Type": 10,  # EntryVideoFile
        # 'HumanReadable': WELCOME_MESSAGE,
        'Contents': 'test1',
    })
    return_results(entry)


if __name__ in ('__main__', '__builtin__', 'builtins'):
    main()