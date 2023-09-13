import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
import time
from time import sleep
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
import re
import tkinter as tk
from tkinter import simpledialog

window = tk.Tk()

window.state("zoomed")

displayText = ""

inputUsername = simpledialog.askstring(title = " ",  prompt = "Enter your NetID: ")
inputPassword = simpledialog.askstring(title = " ", prompt = "Enter your password: ", show = "*")

driver = webdriver.Chrome()
driver.maximize_window()
driver.get('https://zed.rutgers.edu/scheduling/view/')

username = driver.find_element(By.ID, "username")
password = driver.find_element(By.ID, "password") 

username.send_keys(inputUsername)
password.send_keys(inputPassword)

element = driver.find_element(By.NAME, "submit")
element.click()

element = EC.presence_of_element_located((By.ID, "trust-browser-button")) # Used a method that detects the presence of an element because the Duo authentication method can sometimes take a shorter time, or longer time depending on the quality of the Wifi connection
WebDriverWait(driver, 1000).until(element)

element = driver.find_element(By.ID, "trust-browser-button")
element.click()

time.sleep(3)

soup = BeautifulSoup(driver.page_source, features = "html.parser")

dropDown = str(soup.findAll("select", id = "schedule-select"))
dropDownCount = len(re.findall("scheduling", dropDown))

for i in range(dropDownCount): 
    
    dropDown = Select(driver.find_element(By.ID, "schedule-select"))

    prevURL = driver.current_url

    dropDown.select_by_index(i)

    if(i == 0): 
        time.sleep(2) #Used to load the webpage for successful execution of following commands - but often took too long and waited when it wasn't necessary
    else: 
        urlChanges = EC.url_changes(prevURL)
        WebDriverWait(driver, 1000).until(urlChanges) 
    
    soup = BeautifulSoup(driver.page_source, features = "html.parser")

    startTime = soup.find_all("p", class_ = "startTime")
    owner = soup.find_all("p", class_ = "owner")


    campus = soup.find("option", selected = True)

    displayText += "\n" + (campus.text.strip() + ": ") + "\n"

    if(len(owner) == 0 or len(startTime) == 0 or "HD - Level 2 After Hours" in campus.text or "X - OLD - HD" in campus.text): 
        displayText += "\n"
    
    else:
        day = soup.find_all("th")

        dayIndex = -1

        column = soup.find_all("td")

        scheduleColumnCollection = soup.find_all("div", class_ = "scheduleColumn")

        columnCounter = 0

        dayCount = 0
        ownerTimeCount = 0
        for i in range(len(scheduleColumnCollection)):  
            if(dayCount > 6): 
                break
            else: 
                colspanCount = int(day[dayCount].get("colspan"))
                for a in range(colspanCount):
                    childrenNum = len((scheduleColumnCollection[columnCounter]).findChildren("div", recursive = False))
                    if(childrenNum == 0):
                        columnCounter += 1
                        continue
                    else: 
                        for b in range(childrenNum): 
                            displayText += ("Day: " + day[dayCount].text.strip() + " - Owner: " + owner[ownerTimeCount].text.strip() + " - Start Time: " + startTime[ownerTimeCount].text.strip() + "\n")
                            ownerTimeCount += 1
                    columnCounter += 1
                dayCount += 1
        displayText += "\n"
driver.quit()

textWindow = tk.Text(window, name = " ", width=3000, height = 3000)

scroll = tk.Scrollbar(window)

scroll.pack(side=tk.RIGHT)

textWindow.pack(side=tk.LEFT)

textWindow.insert(tk.END, displayText)

window.mainloop()
