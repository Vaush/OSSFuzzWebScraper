import json
import os
from os import path
import threading
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException


def get_shadow_root(self: WebElement) -> WebElement:
    return self.parent.execute_script("return arguments[0].shadowRoot", self)


def get_version_info(driver, url, save_dir, id_list, log_file, thread_id):
    i = 0
    prev_i = 0
    bugs = []
    original_start_time = datetime.now()
    start_time = original_start_time
    try:
        for bug_id in id_list:
            successful = False
            while not successful:
                now = datetime.now()
                try:
                    successful = True
                    if path.exists(save_dir + "/" +  str(bug_id)):
                        f = open(save_dir + "/" + str(bug_id))
                        arr = [x for x in f if x != "\n"]
                        f.close()
                        #print(arr)
                    else:
                        now = datetime.now()
                        while ((now-start_time)*2).seconds < 3:
                            now = datetime.now()
                        start_time = now
                        driver.get(url + str(bug_id))
                        javascript = 'return document.getElementsByTagName("mr-app")[0].shadowRoot'
                        element: WebElement = driver.execute_script(javascript)
                        element = element.find_element_by_tag_name("mr-issue-page").get_shadow_root()
                        issuedet: WebElement = WebDriverWait(element, 60).until(EC.presence_of_element_located((By.TAG_NAME, "mr-issue-details"))).get_shadow_root()
                        issuedet: WebElement = issuedet.find_element_by_tag_name("mr-description").get_shadow_root().find_element_by_tag_name("mr-comment-content").get_shadow_root()
                        WebDriverWait(issuedet, 60).until(EC.presence_of_element_located((By.TAG_NAME, "span")))
                        text = issuedet.get_attribute("innerHTML")
                        soup = BeautifulSoup(text)
                        arr = [x for x in soup.stripped_strings]
                    bug = {}
                    is_regressed = False
                    for el in arr:
                        if is_regressed:
                            is_regressed = False
                            bug["regressed"] = el.strip()
                        elif "Job Type: " in el:
                            bug["job_type"] = el.split(":")[-1].strip()
                        elif "Crash Type: " in el:
                            bug["crash_type"] = el.split(":")[-1].strip()
                        elif "Recommended Security Severity: " in el:
                            bug["sec_sev"] = el.split(":")[-1].strip()
                        elif "Regressed:" in el:
                            is_regressed = True
                        elif "Target: " in el:
                            bug["target"] = el.split(":")[-1].strip()
                    i += 1
                    if (i - prev_i) % 100 == 0:
                        prev_i = i
                        print("Thread " + str(thread_id) + ": " + str(i) + " bugs analysed")
                    bug["id"] = bug_id
                    save_file = open(save_dir + "/" + bug_id, "w+")
                    for x in arr:
                        save_file.write(x + "\n")
                    save_file.close()
                    if "regressed" not in bug:
                        log_file.write(bug_id + " ignored\n")
                        log_file.write(str(arr) + "\n")
                        continue
                    log_file.write(bug_id + " taken\n")
                    bugs.append(bug)
                except Exception as ex:
                    log_file.write("Retrying " + bug_id + "\n")
                    template = "An exception of type {0} occurred. Arguments:\n{1!r}"
                    message = template.format(type(ex).__name__, ex.args)
                    print(message)
                    print("Retrying " + bug_id + " - " + str(original_start_time) + " - " + str(now) + "\n")
                    successful = False

    finally:
        log_file.close()  
    return bugs

def get_bugs_ids(driver, urls):
    content = []
    for url in urls:
        total = 1
        start = 0
        while start < total:
            driver.get(url + str(start))
            javascript = 'return document.getElementsByTagName("mr-app")[0].shadowRoot.querySelector("main > mr-list-page").shadowRoot;'
            element: WebElement = driver.execute_script(javascript)
            issuelist: WebElement = WebDriverWait(element, 60).until(EC.presence_of_element_located((By.TAG_NAME, "mr-issue-list")))
            if start == 0:
                val: str = element.find_elements_by_class_name("issue-count")[0].get_attribute("innerHTML")
                total = int(val.strip().split(" ")[-1])
                print(total)
            issuelist: WebElement = issuelist.get_shadow_root()
            contentlist = issuelist.find_elements_by_class_name("col-id")
            content += [x.text for x in contentlist]
            string = str(start) + " to "
            start += len(contentlist)
            string += str(start)
            print(string)
    r = list(set(content))
    print(str(len(r)) + " ids found")
    return r


def get_bugs_thread(path, id_list, chromedriver_path, thread_id):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    print(chromedriver_path)
    driver = webdriver.Chrome(executable_path=os.path.abspath(chromedriver_path), options=chrome_options)
    log_file = open(path + ".log", "w+")
    bugs = get_version_info(driver, "https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=", "./saved_bugs", id_list, log_file, thread_id)
    file = open(path, "w+")
    json.dump(bugs, file)
    file.close()

cpus = os.cpu_count()-1
cpus = 1
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=os.path.abspath("./chromedriver"), options=chrome_options)
#url = "https://bugs.chromium.org/p/oss-fuzz/issues/list?q=type%3DBug%2CBug-Security&can=1&colspec=ID&start="
urls = ["https://bugs.chromium.org/p/oss-fuzz/issues/list?q=Type%3DBug-Security%20-status%3Aduplicate%2Cwontfix%20asan%20label%3Areproducible%20label%3AClusterFuzz&can=1&start=","https://bugs.chromium.org/p/oss-fuzz/issues/list?q=Type%3DBug-Security%20-status%3Aduplicate%2Cwontfix%20%20label%3Areproducible%20label%3AClusterFuzz&can=1&start=","https://bugs.chromium.org/p/oss-fuzz/issues/list?sort=-reported&q=-status%3Aduplicate%2Cwontfix%20asan%20label%3Areproducible%20label%3AClusterFuzz%20-timeout%20-out-of-memory%20-stack-overflow%20-unexpected-exit%20-indirect-leak%20-direct-leak&can=1&start=","https://bugs.chromium.org/p/oss-fuzz/issues/list?sort=-reported&q=-status%3Aduplicate%2Cwontfix%20ubsan%20label%3Areproducible%20label%3AClusterFuzz%20-timeout%20-out-of-memory&can=1&start="]
setattr(WebElement, 'get_shadow_root', get_shadow_root)
id_list = get_bugs_ids(driver, urls)
n = int(len(id_list)/cpus)
id_lists = [id_list[i:i + n] for i in range(0, len(id_list), n)]
i = 1
thread_list = []
for el in id_lists:
    thread_list.append(threading.Thread(target=get_bugs_thread, args=("bugs_" + str(i), el, "./chromedriver_" + str(i), i)))
    thread_list[-1].start()
    print("Thread " + str(i) + " started")
    i += 1

for thread in thread_list:
    thread.join()
