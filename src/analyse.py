import json
import sys
from sortedcontainers import SortedDict
file = open("bugs_1")
bugs_by_project = {}
bugs = json.load(file)
for bug in bugs:
    if "target" not in bug:
        continue
    project = bug["job_type"].split("_")[-1]
    target = bug["target"]
    if project == "llvm":
        continue
    if project not in bugs_by_project:
        bugs_by_project[project] = {}
    if target not in bugs_by_project[project]:
        bugs_by_project[project][target] = SortedDict()
    versions = bug["regressed"].split("=")[-1].split(":")
    if versions[0] not in bugs_by_project[project][target]:
        bugs_by_project[project][target][versions[0]] = []
    if versions[1] not in bugs_by_project[project]:
        bugs_by_project[project][target][versions[1]] = []
for bug in bugs:
    if "target" not in bug:
        continue
    project = bug["job_type"].split("_")[-1]
    versions = bug["regressed"].split("=")[-1].split(":")
    target = bug["target"]
    if project == "llvm":
        continue
    for version in bugs_by_project[project][target].irange(versions[0], versions[1]):
        bugs_by_project[project][target][version].append(bug)
    if versions[0] == versions[1]:
        bugs_by_project[project][target][versions[0]].pop()
max_per_project = {}
for project in bugs_by_project:
    for target in bugs_by_project[project]:
        max_bugs = ("",[])
        for version in bugs_by_project[project][target]:
            bugs_num = len(bugs_by_project[project][target][version])
            print(project + " " + target + " " + version + " " + str(bugs_num))
            if bugs_num >= len(max_bugs[1]):
                max_bugs = (version, bugs_by_project[project][target][version])
        max_per_project[(project,target)] = max_bugs
file.close()
file = open("max_bugs_num", "w+")
towrite = {}
for (project, target), (version, num) in max_per_project.items():
    file.write(project + " " + target + " " + version + " " + str(len(num)) + "\n")
    if project not in towrite:
        towrite[project] = {}
    towrite[project][target] = {version: num}
file.close()
file = open("max_bugs", "w+")
json.dump(towrite, file)
file.close()



