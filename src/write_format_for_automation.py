import json
file = open("bugs_selection")
arr = json.load(file)
           
file = open("bugs_selection_format_for_automation","w+")
for project in arr:
    for target in arr[project]:
        for version in arr[project][target]:
            commits = []
            bug_num = len(arr[project][target][version])
            for commit in arr[project][target][version][0]["hashes"]:
                if commit == "Afl" or commit == "Libfuzzer":
                    continue
                value = arr[project][target][version][0]["hashes"][commit]
                if commit.lower() == project:
                    commits = [(commit.lower(), value)]
                    break
                commits.append((commit.lower(), value))
            if len(commits) == 0:
                print(project + " " + target + " " + version + " has no commits, aborting")
                file.close()
                exit()
            if len(commits) > 1:
                prompt_string = project + " " + target + " " + version + " has multiple commits and it has not been possible to determine the main one. Please select it among the following:"
                for  i,(commit, value) in  enumerate(commits,1):
                    prompt_string += "\n  " +str(i) + ". " + commit + ": " + value
                val = int(input(prompt_string + "\nIndex: "))
                commits = [commits[val-1]]
            file.write(project + " " + target + " " + version[0:4] + "-" + version[4:6] + "-" + version[6:8] + "T" + version[8:10] + ":" + version[10:12] + " " + commits[0][1] + " " + commits[0][0] + " " + str(bug_num) + "\n")
file.close()

