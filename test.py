import os
import json
import sys

PROJECT_PATH = "{}/tests".format(os.getcwd())
ALL_TESTS_PATH = "./tests/units/"

data = json.load(open('tests/config.json'))
data['PROJECT_PATH'] = PROJECT_PATH
with open('tests/config.json', 'w') as outfile:
    json.dump(data, outfile, indent=4)


def show_tests():
    return [x for x in os.listdir(ALL_TESTS_PATH) if x != "build" and os.path.isdir(ALL_TESTS_PATH + x)]

def test(name: str):
    TEST_DIR = ALL_TESTS_PATH + name + "/{}"
    os.system("cp -R {} {}".format(TEST_DIR.format("src/"), TEST_DIR.format("tmp/")))

    data = json.load(open('tests/config.json'))
    data['PROJECT_PATH'] = PROJECT_PATH
    data['BUILD_COMMAND'] = "./gradlew :units:{}:build -x test".format(name)
    with open('tests/config.json', 'w') as outfile:
        json.dump(data, outfile, indent=4)
    os.system("python3 run.py loop tests/config.json")

    os.system("mv {} {}".format(TEST_DIR.format("src/"), TEST_DIR.format("out/")))
    os.system("mv {} {}".format(TEST_DIR.format("tmp/"), TEST_DIR.format("src/")))
    

def test_all():
    pass

COMMAND = sys.argv[1]
if(COMMAND == "tests"):
    print("All tests are:")
    for test in show_tests():
        print(test)
elif(COMMAND == "test"):
    if(len(sys.argv) == 3):
        test(sys.argv[2])
    else:
        test_all()

