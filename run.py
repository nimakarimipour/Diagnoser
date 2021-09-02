import os
import sys
import json
import shutil
import time

data = json.load(open('config.json'))
build_command = "cd " + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND']
out_dir = "/tmp/NullAwayFix"
delimiter = "$*$"


if(len(sys.argv) != 2):
    raise ValueError("Needs one argument to run: diagnose/apply/pre/loop/clean")

EXPLORER_CONFIG = json.load(open('template.config'))


def load_csv_to_dict(path):
    ans = []
    csvFile = open(path, 'r')
    lines = csvFile.readlines()
    keys = lines[0].strip().split(delimiter)
    for line in lines[1:]:
        item = {}
        infos = line.strip().split(delimiter)
        for i in range(0, len(keys)):
            item[keys[i]] = infos[i]
        ans.append(item)
    return ans

def make_explorer_config(config):
    with open('/tmp/NullAwayFix/explorer.config', 'w') as outfile:
        json.dump(config, outfile)


def delete(file):
    try:
        os.remove(file)
    except OSError:
        pass 

def uprint(message):
    print(message, flush=True) 
    sys.stdout.flush()  

def clean(full=True):
    uprint("Cleaning...")
    delete(out_dir + "/diagnose_report.json")
    delete(out_dir + "/fixes.csv")
    delete(out_dir + "/diagnose.json")
    delete(out_dir + "/cleaned.json")
    delete(out_dir + "/init_methods.json")
    delete(out_dir + "/method_info.csv")
    delete(out_dir + "/history.json")
    delete(out_dir + "/errors.csv")
    if(full):
        delete(out_dir + "/reports.json")
    uprint("Finished.")

def prepare():
    uprint("Diagnose:-In prepare...")
    if not os.path.exists(out_dir):
        uprint("Creating out_dir...")
        os.makedirs(out_dir)
    else:
        uprint("out_dir already exists.")
    uprint("Diagnose:-In prepare finished.")

def pre():
    uprint("Started preprocessing task...")
    uprint("Removing old files...")
    method_path = out_dir + "/method_info.csv"
    delete(method_path)
    delete(out_dir + "/init_methods.json")
    uprint("Removed.")
    uprint("Building project...\n" + build_command)
    new_config = EXPLORER_CONFIG.copy()
    new_config['SUGGEST']['ACTIVE'] = True
    new_config['MAKE_METHOD_INHERITANCE_TREE'] = True
    new_config['MAKE_CALL_GRAPH'] = True
    new_config['MAKE_FIELD_GRAPH'] = True
    new_config['LOG_ERROR']['ACTIVE'] = True
    new_config['LOG_ERROR']['DEEP'] = True
    new_config['ANNOTATION']['NULLABLE'] = data['ANNOTATION']['NULLABLE']
    new_config['ANNOTATION']['NONNULL'] = data['ANNOTATION']['NONNULL']
    make_explorer_config(new_config)
    os.system(build_command + " > /dev/null 2>&1")
    uprint("Built.")
    uprint("Analyzing suggested fixes...")
    fixes = load_csv_to_dict(out_dir + "/fixes.csv")
    uprint("Detecting uninitialized class fields...")
    field_no_inits = [x for x in fixes if (x['reason'] == 'FIELD_NO_INIT' and x['location'] == 'CLASS_FIELD')]
    uprint("found " + str(len(field_no_inits)) + "fields.")
    uprint("Analyzing method infos...")
    methods = load_csv_to_dict(method_path)
    init_methods = {"fixes": []}
    uprint("Selecting appropriate method for each class field...")
    for field in field_no_inits:
        uprint("Analyzing class field: " + field['param'])
        candidate_method = None
        max = 0 
        for method in methods:
            if(method['class'] == field['class']):
                if(field['param'] in method['fields'] and len(method['fields']) > max):
                    candidate_method = method.copy()
                    max = len(method['fields'])
        if(candidate_method != None):
            del candidate_method['fields']
            candidate_method['location'] = "METHOD_RETURN"
            candidate_method['inject'] = True
            candidate_method['annotation'] = data['ANNOTATION']['INITIALIZE']
            candidate_method['param'] = ""
            candidate_method['reason'] = "Initializer"
            candidate_method['pkg'] = ""
            if(candidate_method not in init_methods['fixes']):
                uprint("Selected method: " + candidate_method['method'])
                init_methods['fixes'].append(candidate_method)
            else:
                uprint("Already chosen.")
    with open(out_dir + "/init_methods.json", 'w') as outfile:
        json.dump(init_methods, outfile)
    uprint("Finished detecting methods.")
    uprint("Passing to injector to annotate...")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + out_dir + "/init_methods.json")
    uprint("Annotated.\nFinished.")

def diagnose(optimized):
    optimized = "true" if optimized else "false"
    new_config = EXPLORER_CONFIG.copy()
    new_config['SUGGEST']['ACTIVE'] = True
    new_config['LOG_ERROR']['ACTIVE'] = True
    new_config['LOG_ERROR']['DEEP'] = True
    new_config['ANNOTATION']['NULLABLE'] = data['ANNOTATION']['NULLABLE']
    new_config['ANNOTATION']['NONNULL'] = data['ANNOTATION']['NONNULL']
    make_explorer_config(new_config)
    uprint("Started diagnose task...")
    uprint("Making build command for project...")
    build_command = '"cd ' + data['PROJECT_PATH'] + " && " + data['BUILD_COMMAND'] + '"'
    uprint("Detected build command: " + build_command)
    uprint("Diagnosing...")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar diagnose " + out_dir + " " + build_command + " " + str(data['DEPTH']) + " " + data['ANNOTATION']['NULLABLE'] + " " + optimized)
    uprint("Finsihed.")
    if(data['FORMAT'] != ""):
        os.system("cd " + data['PROJECT_PATH'] + " && " + data['format'])

def apply():
    delete(out_dir + "/cleaned.json")
    uprint("Analyzing diagnose report...")
    report_file = open(out_dir + "/diagnose_report.json")
    reports = json.load(report_file)
    cleaned = {}
    uprint("Selecting effective fixes...")
    cleaned['fixes'] = [fix for fix in reports['reports'] if fix['jump'] < 1]
    uprint("Selected effective fixes.")
    with open(out_dir + "/cleaned.json", 'w') as outfile:
        json.dump(cleaned, outfile)
    uprint("Applying fixes at location: " + out_dir + "/cleaned.json")
    os.system("cd jars && java -jar NullAwayAutoFixer.jar apply " + out_dir + "/cleaned.json")

def loop():
    uprint("Executing loop command")
    finished = False
    while(not finished):
        uprint("Executing (optimized) diagnose task...")
        diagnose(True)
        uprint("Diagnsoe task finished, applying effective fixes...")
        apply()
        uprint("Applied.")
        uprint("Adding diagnosed fixes to history.")
        new_fixes = json.load(open(out_dir + "/diagnose.json"))
        old_fixes = json.load(open(out_dir + "/history.json"))
        old_size = len(old_fixes['fixes'])
        for fix in new_fixes['fixes']:
            if fix not in old_fixes['fixes']:
                old_fixes['fixes'].append(fix)
        new_size = len(old_fixes['fixes'])
        uprint("Fished adding diagnosed fixes to history.")
        with open(out_dir + "/history.json", 'w') as outfile:
            json.dump(old_fixes, outfile)
            outfile.close()
        new_reports = json.load(open(out_dir + "/diagnose_report.json"))
        old_reports = json.load(open(out_dir + "/reports.json"))
        for report in new_reports['reports']:
            if report not in old_reports['reports']:
                old_reports['reports'].append(report)
        with open(out_dir + "/reports.json", 'w') as outfile:
            json.dump(old_reports, outfile)
            outfile.close()
        if(new_size == old_size):
            finished = True
            uprint("No changes, shutting down.")
        else:
            uprint("Getting ready for next round...")
        finished = True
    clean(full=False)

command = sys.argv[1]
prepare()
if(command == "pre"):
    pre()
elif(command == "diagnose"):
    diagnose(False)
elif(command == "apply"):
    apply()
elif(command == "loop"):
    clean()
    pre()
    history = open(out_dir + "/history.json", "w")
    empty = {"fixes": []}
    json.dump(empty, history)
    history.close()
    reports = open(out_dir + "/reports.json", "w")
    empty = {"reports": []}
    json.dump(empty, reports)
    reports.close()
    start = time.time()
    loop()
    end = time.time()
    print("Elapsed time in seconds: " + str(end - start))
elif(command == "clean"):
    clean()
    delete_folder = input("Delete " +  out_dir + " directory too ? (y/n)\n")
    if(delete_folder.lower() in ["yes", "y"]):
        try:
            shutil.rmtree(out_dir)
        except:
            uprint("Failed to remove directory: " + out_dir) 
elif(command == "reset"):
    clean()
    try:
        shutil.rmtree(out_dir)
    except:
        uprint("Failed to remove directory: " + out_dir) 

else:
    raise ValueError("Unknown command.")
    