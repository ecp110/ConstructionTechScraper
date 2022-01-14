from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import requests
import time
import csv
import re

# Search page limit for each search query
page_limit = 6

# Username and Password for LinkedIn
username = "sbob76878@gmail.com"
password = "TESTscript101"

# Key locations to filter for
key_locations = [
    "NSW", "ACT", "QLD", "WA", "NT", "SA", "VIC", "TAS",
    "New South Wales", "Australian Capital Territory",
    "Queensland", "Western Australia", "Northern Territory",
    "South Australia", "Victoria", "Tasmania", "Australia",
    "Sydney", "Melbourne", "Adelaide", "Brisbane", "Perth", "Darwin",
    "Canberra", "Hobart", "Newcastle", "Woolongong", "Gold Coast",
    "Townsville", "Cairns", "Geelong", "Launceston",
    "Auckland", "Wellington", "Dunedin", "Christchurch", "Rotorua",
    "New Zealand"
]

# Company class - stores all information about a company
class Company:
    name = "N/A"
    location = "N/A"
    size = "N/A"
    revenue = "N/A"
    ebitda = "N/A"
    num_offices = "N/A"
    ceo = "N/A"
    cto = "N/A"
    cfo = "N/A"
    website = "N/A"
    phonenum = "N/A"
    email = "N/A"    
    info = "N/A"
    financial_link = "N/A"
    
    def __init__(self, name, location, size, website, info, num_offices, phonenum):
        self.name = name
        self.location = location
        self.size = size
        self.website = website
        self.info = info
        self.num_offices = num_offices
        self.phonenum = phonenum

# Main function for logging in to LinkedIn
# Starts Selenium instance and uses global username and password to login
# Returns Selenium driver instance
def login():
    driver = webdriver.Safari()
    driver.get("https://www.linkedin.com/login/")
    time.sleep(2)

    uBox = driver.find_element_by_id("username")
    uBox.send_keys(username)
    time.sleep(1)

    pBox = driver.find_element_by_id("password")
    pBox.send_keys(password)
    time.sleep(1)

    submit = driver.find_element_by_class_name("login__form_action_container")
    submit.click()
    time.sleep(2)

    return driver

def main_loop():
    # Login and retrieve driver
    driver = login()
    
    # Instatiate list for company linkedin links
    company_links = []

    # First link is searching "technology" within construction industry
    # Second link is searching "construction" within technology industry
    base_search_links = [
        "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22101452733%22%2C%22105490917%22%5D&companySize=%5B%22D%22%2C%22E%22%2C%22F%22%2C%22G%22%2C%22H%22%2C%22I%22%5D&industry=%5B%2248%22%5D&keywords=technology&origin=FACETED_SEARCH&page={}&sid=rfA",
        "https://www.linkedin.com/search/results/companies/?companyHqGeo=%5B%22105490917%22%2C%22101452733%22%5D&companySize=%5B%22D%22%2C%22E%22%2C%22F%22%2C%22G%22%2C%22H%22%2C%22I%22%5D&industry=%5B%2296%22%5D&keywords=construction&origin=FACETED_SEARCH&page={}&sid=QXI"
    ]

    # Pull company links from the search links above
    # Store each company in company_links list
    for base_search_link in base_search_links:
        i = 1
        while i <= page_limit:
            search_link = base_search_link.format(i)

            driver.get(search_link)
            time.sleep(3)
            src = driver.page_source
            soup = BeautifulSoup(src, "lxml")

            for a_tag in soup.find_all("a", class_ = "app-aware-link"):
                link = str(a_tag.get("href"))
                if link not in company_links:
                    company_links.append(link)

            i += 1

    driver.close()
    soup = BeautifulSoup(src, "lxml")

    # Removes any non-company results (eg job listings) that Linkedin returned
    for link in company_links:
        search = re.search(".*company.*", link)
        if search == None:
            company_links.remove(link)
    
    # Redirects all links to the company about page
    x = 0
    while x < len(company_links):
        company_links[x] = company_links[x].strip("/") + "/about/"
        x += 1

    # Re-logs in and pulls new driver instance
    driver = login()

    # Iterates through each company profile, pulling the relevant information
    # Company information is stored in companies list as Company objects
    error_log = []
    companies = []
    for company in company_links:
        driver.get(company)
        time.sleep(3)
        
        src = driver.page_source
        soup = BeautifulSoup(src, "lxml")
        
        # Location (HQ) of Company
        try:
            t = soup.find_all("div", class_= "org-top-card-summary-info-list__info-item")
            location = t[1].text.strip()
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            location = "N/A"

        # Name of Company
        try:
            name = soup.find("h1", class_="t-24 t-black t-bold full-width").text.strip()
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            name = "N/A"
        
        # Number of Employees (size) of Company
        try:
            size = soup.find("dd", class_ = "text-body-small t-black--light mb1").text.strip()
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            size = "N/A"

        # Website of Company
        try:
            website = soup.find("a", class_ = "link-without-visited-state ember-view").text.strip()
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            website = "N/A"

        # Information / Summary of Company
        try:
            info = soup.find("p", class_ = "org-top-card-summary__tagline t-16 t-black").text.strip()
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            info = "N/A"

        # Number of Offices
        try:
            num_offices = soup.find("h3", class_ = "t-20 t-bold").text.strip()
            x = 0
            locs = ""
            while x < len(num_offices):
                if num_offices[x] == "(":
                    y = x + 1
                    while num_offices[y] != ")":
                        locs += num_offices[y]
                        y += 1

                x += 1
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            locs = "N/A"

        # Telephone of Company
        try:
            phonenum = "N/A"
            for i in soup.find_all("a"):
                i = i.get("href")
                if re.search(".*tel.*", str(i)) != None:
                    phonenum = re.search(".*tel.*", str(i)).group().strip("tel:")
        except Exception as e:
            error_log.append("{} | {}".format(company, e))
            phonenum = "N/A"
            
        companies.append(Company(name, location, size, website, info, locs, phonenum))

    driver.close()

    # Cleaning companies to be located in ANZ
    x = 0
    while x < len(companies):
        company = companies[x]
        loc = company.location
        valid = False
        for keyword in key_locations:
            regex = ".*{}.*".format(keyword)
            search = re.search(regex, loc)
            if search != None:
                valid = True
        
        if not valid:
            companies.pop(x)
            continue
        x += 1

    ####
    # Not working - potential way to get to financial information#
    ####
    # Linking to potential financials source

    #base_dnb_link = "https://www.dnb.com"
    #financial_search_link = "https://www.dnb.com/business-directory/top-results.html?term={}&page=1"
    
    #for company in companies:
    #    driver = webdriver.Safari()
    #    name = company
    #    # Adjusts link to company name
    #    financial_search_link = financial_search_link.format(company.name)
    #
    #    # Accesses page with search as company name
    #    driver.get(financial_search_link)
    #    soup = BeautifulSoup(driver.page_source, "lxml")
    #    time.sleep(1)
    #    # Pulls top search result and stores back into company object
    #    try:
    #        company_link = "{}{}".format(base_dnb_link, soup.find_all("li", class_ = "row search_result")[1].find("a").get("href"))
    #        company.financial_link = company_link
    #    except Exception as e:
    #        error_log.append("{} | {}".format(name, e))
    #        driver.close()
    #        continue
    #
    #    driver.close()

    # Writes company output to CSV
    with open("output.csv", "w+", encoding = "UTF-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Name","Headquarters","Num Employees","Rev","EBITDA","Num Offices","CEO","CTO","CFO","Website","Phone Number","Email Address","Solution/Info","Financials Link"])
        for company in companies:
            writer.writerow([
            company.name, company.location, company.size, company.revenue, company.ebitda,
            company.num_offices, company.ceo, company.cto, company.cfo, company.website,
            company.phonenum, company.email, company.info, company.financial_link
            ])


if __name__ == "__main__":
    main_loop()