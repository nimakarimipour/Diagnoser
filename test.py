import os
import json

PROJECT_PATH = "{}/tests".format(os.getcwd())

data = json.load(open('tests/config.json'))
data['PROJECT_PATH'] = PROJECT_PATH
with open('tests/config.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)

os.system("python3 run.py loop tests/config.json")