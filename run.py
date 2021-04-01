import os
import sys
import json

f = open('config.json')
data = json.load(f)
command = "cd " + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND']
fixes_dir = data['FIX_PATH'][0: data['FIX_PATH'].rindex("/")] if "/" in data['FIX_PATH'] else "/"

def delete(file):
    try:
        os.remove(file)
    except OSError:
        pass    

if(len(sys.argv) != 2):
    raise ValueError("Needs one argument to run: diagnose/apply/pre")
arg = sys.argv[1]

if(arg == "pre"):
    print("Removing old files...")
    method_path = fixes_dir + "/method_info.json"
    delete(method_path)
    delete(fixes_dir + "/init_methods.json")
    print("Removed.")
    print("Building project...")
    os.system(command + " > /dev/null 2>&1")
    print("Built.")
    print("Analyzing suggested fixes...")
    fixes_file = open(data['FIX_PATH'])
    fixes = json.load(fixes_file)
    print("Deecting uninitialized class fields...")
    field_no_inits = [x for x in fixes['fixes'] if (x['reason'] == 'FIELD_NO_INIT' and x['location'] == 'CLASS_FIELD')]
    print("found " + str(len(field_no_inits)) + "fields.")
    print("Analyzing method infos...")
    methods = json.load(open(method_path))
    init_methods = {"fixes": []}
    print("Selecting appropriate method for each class field...")
    for field in field_no_inits:
        print("Analyzing class field: " + field['param'])
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
            candidate_method['param'] = ""
            candidate_method['reason'] = "Initializer"
            candidate_method['pkg'] = ""
            if(candidate_method not in init_methods['fixes']):
                print("Selected method: " + candidate_method['method'])
                init_methods['fixes'].append(candidate_method)
            else:
                print("Already chosen.")
    with open(fixes_dir + "/init_methods.json", 'w') as outfile:
        json.dump(init_methods, outfile)
    print("Finished detecting methods.")
    print("Passing to injector to annotate...")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + fixes_dir + "/init_methods.json")
    print("Annotated.\nFinished.")

elif(arg == "diagnose"):
    command = '"cd ' + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND'] + '"'
    os.system("cd jars && java -jar NullAwayAutoFixer.jar diagnose " + data['FIX_PATH'] + " " + command)
    print("FINISHED")
elif(arg == "apply"):
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + fixes_dir + "/diagnose_report.json")

