import os

import json

with open('config.json') as f:
    data = json.load(f)
    command = '"cd ' + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND'] + '"'
    os.system("cd jars && java -jar NullAwayAutoFixer.jar " + data['FIX_PATH'] + " " + command)
    print("FINISHED")
