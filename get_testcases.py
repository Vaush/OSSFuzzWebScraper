import wget
import json
import os
failed_bugs = []
json = json.load(open("bugs_selection"))
for project in json:
    for target in json[project]:
        for version in json[project][target]:
            name = project+"_"+target
            dirname = "testcases/"+name
            os.mkdir(dirname)
            dirname += "/testcases"
            os.mkdir(dirname)
            for bug in json[project][target][version]:
                getNext = False
                bugfile = open("saved_bugs/"+bug["id"])
                arr = [x for x in bugfile if x != "\n"]
                bugfile.close()
                address = None
                for line in arr:
                    if getNext:
                        address = line
                        break;
                    if line == "Reproducer Testcase:\n":
                        getNext = True
                else:
                    failed_bugs.append(bug["id"])
                if address != None:
                    print(bug["id"] + ": " + wget.download(address, dirname +
 "/" + bug["id"] + ".txt"))
print("Failed bugs:\n" + str(failed_bugs))

