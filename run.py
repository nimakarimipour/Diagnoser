import os
import sys
import json

f = open('config.json')
data = json.load(f)
command = "cd " + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND']
fixes_dir = data['FIX_PATH'][0: data['FIX_PATH'].rindex("/")] if "/" in data['FIX_PATH'] else "/"


if(len(sys.argv) != 1):
    raise ValueError("Needs one argument to run: diagnose/apply/pre")
arg = sys.argv[0]
if(arg == "pre"):
    os.system(command)
    fixes_file = open(data['FIX_PATH'])
    fixes = json.load(fixes_file)
    field_no_inits = [x for x in fixes['fixes'] if (x['reason'] == 'FIELD_NO_INIT' and x['location'] == 'CLASS_FIELD')]
    method_path = fixes_dir + "/method_info.json"
    methods = json.load(open(method_path))
    init_methods = []
    for field in field_no_inits:
        candidate_method = None
        max = 0
        for method in methods['infos']:
            if(method['class'] == field['class']):
                if(field['param'] in method['fields'] and len(method['fields']) > max):
                    candidate_method = method.copy()
                    max = len(method['fields'])
        if(candidate_method != None):
            del candidate_method['fields']
            candidate_method['location'] = "METHOD_RETURN"
            candidate_method['inject'] = True
            candidate_method['annotation'] = data['INITIALIZE_ANNOT']
            init_methods.append(candidate_method)
    with open(fixes_dir + "/init_methods.json", 'w') as outfile:
        json.dump(init_methods, outfile)
    print("FINISHED")
elif(arg == "diagnose"):
    command = '"cd ' + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND'] + '"'
    os.system("cd jars && java -jar NullAwayAutoFixer.jar diagnose " + data['FIX_PATH'] + " " + command)
    print("FINISHED")
elif(arg == "apply"):
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + fixes_dir + "/diagnose_report.json")

