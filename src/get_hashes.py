import json
import os
import string

from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait


def get_shadow_root(self: WebElement) -> WebElement:
    return self.parent.execute_script("return arguments[0].shadowRoot", self)


def get_hashes(driver: webdriver, url, version):
    tokens = url.split("=")
    tokens[-1] = version + ":" + version
    url = "=".join(tokens)
    driver.get(url)
    hashes = {}
    print("URL: " + url)
    try:
        trs = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "revisions-info"))).get_shadow_root().find_elements_by_class_name("body")
        for tr in trs:
            elems = tr.find_elements_by_tag_name("span")
            hashes[elems[0].text] = max(elems[2].text, elems[1].text)
    except Exception:
        return None
    return hashes


setattr(WebElement, 'get_shadow_root', get_shadow_root)
chrome_options = Options()
chrome_options.add_argument("--headless")
driver = webdriver.Chrome(executable_path=os.path.abspath("./chromedriver"), options=chrome_options)
file = open("max_bugs")
bugs = json.load(file)

file = open("max_bugs_num_sorted_selection")
bugs_to_get = {}
for line in file:
    tokens = line.split(" ")
    if tokens[0] not in bugs_to_get:
        bugs_to_get[tokens[0]] = {tokens[1]: {tokens[2]: []}}
    else:
        bugs_to_get[tokens[0]][tokens[1]] = {tokens[2]: []}
    prev_bug_set = set()
    for bug in bugs[tokens[0]][tokens[1]][tokens[2]]:
        bug["hashes"] = get_hashes(driver, bug["regressed"], tokens[2])
        if bug["hashes"] is not None:
            if len(prev_bug_set) == 0 or prev_bug_set == set(bug["hashes"]):
                bugs_to_get[tokens[0]][tokens[1]][tokens[2]].append(bug)
                prev_bug_set = set(bug["hashes"])
            else:
                print("Wrong hashes on bug")
        else:
            print("Error retrieving hashes")
    print(line + " done")
file = open("bugs_selection", "w+")
json.dump(bugs_to_get, file)
