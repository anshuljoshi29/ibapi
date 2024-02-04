import streamlit as st
import pymongo
import pandas as pd
import os

store = st.secrets["URL"]
client = pymongo.MongoClient(store)
db = client["ibapiii"]
collection = db["ibapi"]
from selenium import webdriver

from selenium.webdriver.common.by import By

from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException,ElementClickInterceptedException

from selenium.webdriver.chrome.service import Service

from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager

from selenium.webdriver.common.keys import Keys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

import pymongo
import re
from selenium.webdriver.chrome.options import Options
########################################################
options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
options.add_argument('--log-level=3')


time.sleep(2)
def start():
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),options=options)
    driver.get("https://ibapi.in/sale_info_home.aspx")
    def data_scrap(data_text,img,pdf):
        img_str = ', '.join(img)
        pdf_str = ', '.join(pdf)
    
        patterns = {
            "Property Id":r"Property ID:(.+?)\)",
            "Bank Name": r"Bank Name: (.+)",
            "State": r"State: (.+)",
            "District": r"District: (.+)",
            "Reserve Price Rs": r"Reserve Price Rs: (\d+)",
            "EMD Rs": r"EMD Rs: (\d+)",
            "City": r"City: (.+)",
            "Borrower's Name": r"Borrower's Name: (.+)",
            "Owner's Name": r"Owner's Name: (.+)",
            "Ownership Type": r"Ownership Type: (.+)",
            "Summary Description": r"Summary Description: (.+)",
            "Property Type": r"Property Type: (.+)",
            "Property Sub Type": r"Property Sub Type: (.+)",
            "Type of Title Deed": r"Type of Title Deed: (.+)",
            "Status of Possession": r"Status of Possession: (.+)",
            "Auction Open Date": r"Auction Open Date: (.+)",
            "Auction Close Date": r"Auction Close Date: (.+)",
            "Address": r"Address: (.+)",
            "Authorised Officer Detail": r"Authorised Officer Detail : (.+)",
        }
        data = {}
        for key, pattern in patterns.items():
            match = re.search(pattern, data_text)
            if match:
                data[key] = match.group(1)
        data["Images"]=img_str
        data["Pdfs"]=pdf_str
        result = collection.insert_one(data)
        print("success")
    
    count=3
    timeout=5
    try:
        while True:
            a=True
            # property type
            driver.find_element(By.XPATH,'//*[@id="DropDownList_Property_Type"]').click()
            # all property
            driver.find_element(By.XPATH,'//*[@id="DropDownList_Property_Type"]/option[6]').click()
    
    
            # select state 
            driver.find_element(By.XPATH,'//*[@id="DropDownList_State"]').click()
            time.sleep(2)
    
            # andhra pradesh
            driver.find_element(By.XPATH,f'//*[@id="DropDownList_State"]/option[{count}]').click()
            time.sleep(2)
    
            # agree to terms and condition
            driver.find_element(By.XPATH,'//*[@id="chk_term"]').click()
            time.sleep(3)
    
            # search
            driver.find_element(By.XPATH,'//*[@id="Button_search"]').click()
            time.sleep(4)
            while a:
                WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((By.XPATH, '//*[@id="tbl_search"]/tbody/tr')))
                slide = driver.find_element(By.XPATH, '//*[@id="tbl_search"]/tbody/tr')
                driver.execute_script("arguments[0].scrollIntoView({block: 'center', inline: 'center' });",slide)
                
                time.sleep(2)
                # sort
                driver.find_element(By.XPATH,'//*[@id="tbl_search"]/thead/tr/th[7]').click()
                time.sleep(1)
                driver.find_element(By.XPATH,'//*[@id="tbl_search"]/thead/tr/th[7]').click()
                time.sleep(2)
                c=1
                trs = driver.find_elements(By.XPATH, '//*[@id="tbl_search"]/tbody/tr')
                for tr in trs:
                    id = driver.find_element(By.XPATH,f'//*[@id="tbl_search"]/tbody/tr[{c}]/td[1]')
                    query = {'Property Id': id.text}
                    result = collection.find_one(query)
                    if(result):
                        c+=1
                        continue
                    td_element = driver.find_element(By.XPATH,f'//*[@id="tbl_search"]/tbody/tr[{c}]/td[7]')
                    print(td_element.text)
                    if(td_element.text==""):
                        a=False
                        break
                    tr.click()
                    time.sleep(3)
                    data_text=driver.find_element(By.XPATH,'//*[@id="modal_detail"]').text
                    img_values = []
                    pdf_values = []
    
                    for i in range(1,3):
                        try:
                            images = driver.find_element(By.XPATH,f'//*[@id="image_{i}"]')
                            img_value = images.get_attribute('src')
                            img_values.append(img_value)
                        except:
                            pass
                        
                        try:
                            pdfs = driver.find_element(By.XPATH,f'//*[@id="doc_link_{i}"]')
                            pdf_value = pdfs.get_attribute('href')
         
                            pdf_values.append(pdf_value)
                        except:
                            pass
                
                    data_scrap(data_text,img_values,pdf_values)
                    driver.find_element(By.XPATH,'//*[@id="modal_detail"]/div/div/div[1]/button').click()
                    time.sleep(1)
                    c+=1
                try:
                    driver.find_element(By.XPATH,'//*[@id="tbl_search_next"]').click()
                    time.sleep(2)
                    c=1
                except:
                    count=31
                    break
        
    except Exception as e:
        print(e)
    driver.quit()



pipeline = [
    {"$match": {"Property Sub Type": {"$ne": None}}},
    {"$group": {"_id": "$Property Sub Type"}},
    {"$sort": {"_id": 1}}
]
distinct_options = collection.aggregate(pipeline)
options_list = [option["_id"] for option in distinct_options]
options_list.insert(0, 'All')

st.title("Data Viewer")

def fetch_data(query={}):
    cursor = collection.find(query, {"_id": 0}) 
    df = pd.DataFrame(list(cursor))  
    return df
if st.button('Scrap'):
    # Call your function when the button is clicked
    start()
option = st.selectbox(
    'How would you like to be contacted?',
    options_list
)
st.write('You selected:', option)

if option == 'All':
    data = fetch_data()
else:
    data = fetch_data({"Property Sub Type": option})

st.write(data)
