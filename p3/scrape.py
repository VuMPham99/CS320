# project: p3
# submitter: vmpham2
# partner: none
# hours: 1

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium import webdriver
from collections import deque
import os
import pandas as pd
import time
import requests

class GraphSearcher:
    def __init__(self):
        self.visited = set()
        self.order = []

    def go(self, node):
        raise Exception("must be overridden in sub classes -- don't change me here!")

    def dfs_search(self, node):
        # 1. clear out visited set
        self.visited.clear()
        if len(self.order) >0:
            self.order = []
        # 2. start recursive search by calling dfs_visit
        self.dfs_visit(node)

    def dfs_visit(self, node):
        # 1. if this node has already been visited, just `return` (no value necessary)
        if node in self.visited:
            return 
        # 2. mark node as visited by adding it to the set
        self.visited.add(node)
        # 3. add this node to the end of self.order
        self.order.append(node)
        # 4. get list of node's children with this: self.go(node)
        children = self.go(node)
        # 5. in a loop, call dfs_visit on each of the children
        for child in children:
            self.dfs_visit(child)
            
    def bfs_search(self,node):
        self.visited.clear()
        if len(self.order) >0:
            self.order = []
        self.bfs_visit(node)
        
    def bfs_visit(self,node):
        q = deque([node])
        if node in self.visited:
            return
        self.visited.add(node)
        self.order.append(node)
        while len(q)>0:
            cur = q.popleft()
            children = self.go(cur)
            for child in children:
                if child not in self.visited:
                    q.append(child)
                    self.visited.add(child)
                    self.order.append(child)                
            
class MatrixSearcher(GraphSearcher):
    def __init__(self, df):
        super().__init__() # call constructor method of parent class
        self.df = df

    def go(self, node):
        children = []
        # TODO: use `self.df` to determine what children the node has and append them
        for child, has_edge in self.df.loc[node].items():
            if has_edge == 1:
                children.append(child)
        return children
    
class FileSearcher(GraphSearcher):
    def __init__(self):
        super().__init__()
        self.msg = ""
    
    def go(self,file):
        path = os.path.join("./file_nodes",file)
        with open(path,"r") as f:
            data = f.read()
            data = data.split("\n")[:2]
            self.msg += data[0]
            children = data[1].split(",")
        return children
    
    def message(self):
        return self.msg
    
class WebSearcher(GraphSearcher):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.tbl = pd.DataFrame()
    
    def go(self,node):
        self.driver.get(node)
        elem = self.driver.find_element(by = "id", value = "Pages").find_elements(by = "tag name", value = "th")
        children = [i.find_element(by="tag name",value = "a").get_attribute('href') for i in elem]
        df = pd.read_html(self.driver.page_source)[0]
        self.tbl = self.tbl.append(df,ignore_index = True)
        return children
    
    def table(self):
        return self.tbl
        
# download image adopted from https://stackoverflow.com/questions/57055214/downloading-images-using-requests-in-python3
def reveal_secrets(driver, url, travellog):
    pwd = ""
    for i in travellog['clue']:
        pwd += str(i)
    driver.get(url)
    driver.find_element(value = "password").send_keys(pwd)
    driver.find_element(value = "attempt-button").click()
    time.sleep(0.2)
    driver.find_element(value = "securityBtn").click()
    time.sleep(1)
    src = driver.find_element(value = "image").get_attribute("src")
    location = driver.find_element(value = "location").text
    res = requests.get(src)
    assert res.status_code == 200
    with open("Current_Location.jpg","wb") as f: 
        f.write(res.content)
    return location
 