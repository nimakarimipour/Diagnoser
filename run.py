import os
import sys
import json
import shutil

f = open('config.json')
data = json.load(f)
build_command = "cd " + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND']
out_dir = "/tmp/NullAwayFix"

if(len(sys.argv) != 2):
    raise ValueError("Needs one argument to run: diagnose/apply/pre/loop/clean")

def delete(file):
    try:
        os.remove(file)
    except OSError:
        pass    

def clean():
    print("Cleaning...")
    delete(out_dir + "/diagnose_report.json")
    delete(out_dir + "/fixes.json")
    delete(out_dir + "/diagnose.json")
    delete(out_dir + "/cleaned.json")
    delete(out_dir + "/init_methods.json")
    delete(out_dir + "/method_info.json")
    delete(out_dir + "/diagnosed.json")
    print("Finished.")

def prepare():
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)
    f = open(out_dir + "/diagnosed.json", "w")
    json.dump(data, f)

def pre():
    print("Started preprocessing task...")
    print("Removing old files...")
    method_path = out_dir + "/method_info.json"
    delete(method_path)
    delete(out_dir + "/init_methods.json")
    print("Removed.")
    print("Building project...")
    os.system(build_command + " > /dev/null 2>&1")
    print("Built.")
    print("Analyzing suggested fixes...")
    fixes_file = open(out_dir + "/fixes.json")
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
    with open(out_dir + "/init_methods.json", 'w') as outfile:
        json.dump(init_methods, outfile)
    print("Finished detecting methods.")
    print("Passing to injector to annotate...")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + out_dir + "/init_methods.json")
    print("Annotated.\nFinished.")

def diagnose(optimized):
    optimized = "true" if optimized else "false"
    print("Started diagnose task...")
    print("Making build command for project...")
    build_command = '"cd ' + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND'] + '"'
    print("Detected build command: " + build_command)
    print("Diagnosing...")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar diagnose " + out_dir + " " + build_command + " " + optimized)
    print("Finsihed.")

def apply():
    delete(out_dir + "/cleaned.json")
    print("Analyzing diagnose report...")
    report_file = open(out_dir + "/diagnose_report.json")
    reports = json.load(report_file)
    cleaned = {}
    print("Selecting effective fixes...")
    cleaned['fixes'] = [fix for fix in reports['reports'] if fix['jump'] < 1]
    print("Selected effective fixes.")
    with open(out_dir + "/cleaned.json", 'w') as outfile:
        json.dump(cleaned, outfile)
    print("Applying fixes at location: " + out_dir + "/cleaned.json")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + out_dir + "/cleaned.json")


command = sys.argv[1]
prepare()
if(command == "pre"):
    pre()
elif(command == "diagnose"):
    diagnose(False)
elif(command == "apply"):
    apply()
elif(command == "clean"):
    clean()
    delete_folder = input("Delete " +  out_dir + " directory too ? (y/n)\n")
    if(delete_folder.lower() in ["yes", "y"]):
        try:
            shutil.rmtree(out_dir)
        except:
            print("Failed to remove directory: " + out_dir) 

elif(command == "loop"):
    print("Executing loop command")
    finished = False
    while(not finished):
        print("Executing (optimized) diagnose task...")
        diagnose(True)
        print("Diagnsoe task finished, applying effective fixes...")
        apply()
        print("Applied.")
        print("Adding diagnosed fixes to history.")
        new_fixes_file = open(out_dir + "/diagnose.json")
        new_fixes = json.load(new_fixes_file)
        old_fixes_file = open(out_dir + "/diagnosed.json")
        old_fixes = json.load(new_fixes_file)
        old_size = len(old_fixes['fixes'])
        old_fixes['fixes'].append(new_fixes['fixes'])
        new_size = len(old_fixes['fixes'])
        print("Fished adding diagnosed fixes to history.")
        with open(out_dir + "/diagnosed.json", 'w') as outfile:
            json.dump(old_fixes, outfile)
        if(new_size == old_size):
            finished = True
            print("No changes, shutting down.")
        else:
            print("Getting ready for next round...")
else:
    raise ValueError("Unknown command.")
    
