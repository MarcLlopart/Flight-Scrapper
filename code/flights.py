import requests
from bs4 import BeautifulSoup
from selenium.webdriver import Chrome
import time
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import smtplib 
import numpy as np
from email.mime.multipart import MIMEMultipart
#import undetected_chromedriver as uc

#Options
chrome_options = Options() 
chrome_options.add_experimental_option("detach", True)
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)
#For ChromeDriver version 79.0.3945.16 or over
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument("window-size=1280,800")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36")
chrome_options.add_argument("--incognito")

#Setting up driver
path = Service('insert/chromedriver/path')
driver = Chrome(service=path,options=chrome_options)
url = 'https://www.skyscanner.es/'
driver.get(url)

cookies = driver.find_element(by=By.XPATH,value='//*[@id="acceptCookieButton"]') #accept cookies 
cookies.click()

# Ticket types
one_way = '//*[@id="fsc-trip-type-selector-one-way"]'
round_trip = '//*[@id="fsc-trip-type-selector-return"]'

def ticket_type(ticket): 

    try: 
        ticket_type = driver.find_element(by=By.XPATH,value=ticket)
        ticket_type.click()
    except: 
        pass



def departure(city):

    dep_city = driver.find_element(by=By.XPATH,value='//*[@id="fsc-origin-search"]')
    time.sleep(1.5)
    dep_city.send_keys(city)
    time.sleep(1)
    dep_city.send_keys(Keys.ENTER)

def arrival(city): 
    
    arr_city = driver.find_element(by=By.XPATH,value='//*[@id="fsc-destination-search"]')
    time.sleep(1.5)
    arr_city.send_keys(city)
    time.sleep(1)
    arr_city.send_keys(Keys.ENTER)



#Check dates
def dep_dates(month): 

    dep_dates = driver.find_element(by=By.XPATH,value='//*[@id="depart-fsc-datepicker-button"]')
    dep_dates.click()
    time.sleep(1.5)
    dep_dates = driver.find_element(by=By.XPATH,value='//*[@id="depart-fsc-datepicker-popover"]/div/div/div[1]/div/nav/div/div[2]/button')
    dep_dates.click()
    time.sleep(1)
    month_select = driver.find_element(by=By.XPATH,value=f'//*[@id="depart-fsc-datepicker-popover"]/div/div/div[2]/div/button[{month}]')
    month_select.click()



def search_ticket():
    search_button = driver.find_element(by=By.XPATH,value='//*[@id="flights-search-controls-root"]/div/div/form/div[3]/button')
    time.sleep(1)
    search_button.click()


def get_prices(): 
    driver.execute_script("window.scrollTo(0,  document.body.scrollHeight/4)") 
    prices_list = []
    #week 1
    for i in range(4, 8):
        prices = driver.find_element(by=By.XPATH,value=f'//*[@id="app-root"]/div/div/div[1]/div/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/table/tbody/tr[1]/td[{i}]/button/div[2]')
        prices_list.append(prices.text)
    #weeks 2-3
    cont = 2
    i = 1
    while(i<8):
        prices = driver.find_element(by=By.XPATH,value=f'//*[@id="app-root"]/div/div/div[1]/div/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/table/tbody/tr[{cont}]/td[{i}]/button/div[2]')
        prices_list.append(prices.text)  
        i += 1
        if (i == 7):
            i = 1
            cont += 1
            continue
        if (cont == 5): 
            break
    
    for i in range(1, 6):
        prices = driver.find_element(by=By.XPATH,value=f'//*[@id="app-root"]/div/div/div[1]/div/div[3]/div[2]/div[1]/div[2]/div/div[2]/div/div/div/div[2]/div/div/div[2]/table/tbody/tr[5]/td[{i}]/button/div[2]')
        prices_list.append(prices.text)  
    
    return prices_list



def lowest_price(prices): 
    low_price = []
    for i in range(len(prices)): 
        if(prices[i] == '-'):
            prices.append(999)
            continue
        else:    
            low_price.append(int(prices[i].split()[0]))
    return min(low_price), np.argmin(low_price)+1

def connect_mail(username, password):
    global server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(username, password)

def create_msg(price, day, month, year, origin, dest):
    global msg

    msg = 'Subject: {}\n\nCurrent Cheapest flight:\n\nOrigin: {}\nDestination: {}\nPrice: {} EUR\nDate: {}/{}/{}\n'.format(
                    'CURRENT CHEAPEST FLIGHT',
                    origin,
                    dest,
                    price,
                    day,month,year)

def send_email(msg):
    global message
    message = MIMEMultipart()
    message['Subject'] = 'Current Best flight'
    message['From'] = 'sender@email.com'
    message['to'] = 'receiver@email.com'

    server.sendmail('sender@email.com', 'receiver@email.com', msg)





origin = 'Barcelona' #might change in a future
dest = 'Lisboa'
month = 9
year = 2022
with open('pw.txt', 'r') as f: #keep your credentials safe!
    pw = f.read()
sender_mail = 'sender@email.com'
sender_pass = pw
receiver_mail = 'receiver@email.com'

departure(origin)
arrival(dest)
ticket_type(one_way)
dep_dates(7) #month count starts from actual month
search_ticket()
time.sleep(15) #avoid being stopped to be a bot (beta mode)
prices = get_prices()
min_price, day = lowest_price(prices)
connect_mail(sender_mail, pw)
create_msg(min_price, day, month, year, origin, dest)
send_email(msg)
exit()
