from selenium import webdriver
from selenium.common import NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup
import pandas as pd
from unidecode import unidecode
# Please open terminal and write 'pip install openpyxl'

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
driver_path = './chromedriver.exe'

while (True):
    try:
        print("Quit -> 0\nCreate excel File -> 1")
        checker = int(input("Operation :"))

        if checker == 0:
            break

        elif checker == 1:
            city = input("Please enter city name: ")
            district = input("Please enter district name: ")

            city = unidecode(city).lower()
            district = unidecode(district).lower()

            excelFileName = 'satilik-konut-{}-{}'.format(city, district)

            dF = pd.DataFrame(
                columns=['Ilan No', 'Kategori', 'Bina Yasi', 'Binanin Kat Sayisi', 'Tur', 'Net m2', 'Oda Sayisi',
                         'Bulundugu Kat', 'Isitma', 'Krediye Uygunluk', 'Fiyat'])

            browser = webdriver.Chrome(options=options, service=Service(driver_path))
            browser.maximize_window()

            linkValue = "https://www.emlakjet.com/satilik-konut/{}-{}/".format(city, district)  # city, district
            count = None

            while (count != 0):
                browser.get(linkValue)
                current_url = browser.current_url

                source = browser.page_source
                soup = BeautifulSoup(source, 'html.parser')
                homepage = "https://www.emlakjet.com"

                divs = soup.find_all("div", attrs={"class": "_3qUI9q"})
                linkList = []
                allHomeInformations = []

                for div in divs:
                    links = div.find_all("a", attrs={"href": True})
                    for i in links:
                        link = homepage + i['href']
                        linkList.append(link)

                for i in range(len(linkList)):
                    browser.get(linkList[i])

                    try:
                        cookieXPath = '// *[ @ id = "__next"] / div[4] / div[3] / div[2] / div / button'
                        browser.find_element(By.XPATH, cookieXPath).click()
                    except NoSuchElementException:
                        pass

                    try:
                        showMoreXPath = '//*[@id="bilgiler"]/div/div[2]/div/div[2]'
                        showMoreXPathElement = browser.find_element(By.XPATH, showMoreXPath)
                        actionChains = ActionChains(browser)
                        actionChains.move_to_element(showMoreXPathElement).click().perform()
                    except NoSuchElementException:
                        pass

                    homeInfos = []
                    try:
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='İlan Numarası']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Kategorisi']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Binanın Yaşı']/following-sibling::*").text)
                        homeInfos.append(browser.find_element(By.XPATH,
                                                              "//*[text()='Binanın Kat Sayısı']/following-sibling::*").text)
                        homeInfos.append(browser.find_element(By.XPATH, "//*[text()='Türü']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Net Metrekare']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Oda Sayısı']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Bulunduğu Kat']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Isıtma Tipi']/following-sibling::*").text)
                        homeInfos.append(
                            browser.find_element(By.XPATH, "//*[text()='Krediye Uygunluk']/following-sibling::*").text)
                        pricePath = browser.find_element(By.XPATH,
                                                         '//*[@id="__next"]/div[3]/div[2]/div[2]/div[2]/div[1]/div').text
                        priceLength = browser.find_element(By.XPATH,
                                                           '//*[@id="__next"]/div[3]/div[2]/div[2]/div[2]/div[1]/div').text.find(
                            "L")

                        price = ''
                        for j in range(0, priceLength + 1):
                            price += pricePath[j]
                        homeInfos.append(price)

                    except NoSuchElementException:
                        print("Inappropriate data !")

                    allHomeInformations.append(homeInfos)

                    if i == len(linkList) - 1:
                        for m in range(len(allHomeInformations)):
                            item = allHomeInformations[m]
                            if len(item) == 11:
                                dF = dF._append(
                                    {'Ilan No': item[0], 'Kategori': item[1], 'Bina Yasi': item[2],
                                     'Binanin Kat Sayisi': item[3],
                                     'Tur': item[4], 'Net m2': item[5], 'Oda Sayisi': item[6],
                                     'Bulundugu Kat': item[7], 'Isitma': item[8], 'Krediye Uygunluk': item[9],
                                     'Fiyat': item[10]}, ignore_index=True)
                            else:
                                pass

                        allHomeInformations = []
                        linkList = []
                        browser.get(current_url)

                        try:
                            cookieXPath = '// *[ @ id = "__next"] / div[4] / div[3] / div[2] / div / button'
                            browser.find_element(By.XPATH, cookieXPath).click()
                        except NoSuchElementException:
                            pass

                        try:
                            nextPageButtonElement = browser.find_element(By.CSS_SELECTOR, 'li.OTUgAO')
                        except NoSuchElementException:
                            print("All datas are writing to excel file please wait !")
                            dF.to_excel(r'./{}.xlsx'.format(excelFileName))
                            count = 0

                        try:
                            actionChains = ActionChains(browser)
                            actionChains.move_to_element(nextPageButtonElement).click().perform()
                            current_url = browser.current_url
                            linkValue = current_url
                        except StaleElementReferenceException:
                            pass

        else:
            print("Unknown Error please try again!")

    except ValueError:
        print("Please press 1 or 0")




