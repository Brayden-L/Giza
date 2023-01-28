from bs4 import BeautifulSoup
import lxml
import cchardet
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
import re

url_str = "https://www.mountainproject.com/route/stats/105725659/heart-of-darkness"

firefoxOptions = Options()
# firefoxOptions.add_argument("--headless")
service = Service(GeckoDriverManager().install())
driver = webdriver.Firefox(
    options=firefoxOptions,
    service=service,
)
driver.implicitly_wait(2)
butt_xpath = """//*[@id="route-stats"]/div[3]/div/div[4]/div/div/button"""

driver.get(url_str)
while True:
    try:
        butt = driver.find_element(By.XPATH, butt_xpath)
        butt.click()
    except:
        break

res = driver.page_source

name = []
namelink = []
entrydate = []
pitches = []
style = []
lead_style = []
comment = []
if res is None:
    d = None
else:
    soup = BeautifulSoup(res, "lxml")
    # print(soup.select("#route-stats > div.row.pt-main-content > div > h1")) # Tells you which page is being scraped, useful for debugging
    try:
        blocks = list(
            soup.select(
                "#route-stats > div.onx-stats-table > div > div.col-lg-6.col-sm-12.col-xs-12.mt-2.max-height.max-height-md-1000.max-height-xs-400 > div > table > tbody"
            )[0].find_all("tr")
        )
    except Exception as e:
        print(e)
        blocks = []
    for x in blocks:
        soup = BeautifulSoup(str(x), "lxml")
        entries = soup.find_all("div", attrs={"class": None})
        for entry in entries:
            entrytext = entry.text
            try:
                name.append(soup.find("a").text.strip())
            except Exception:
                name.append("")

            try:
                namelink.append(soup.find("a")["href"].strip())
            except Exception:
                namelink.append("")

            try:
                date_search = [re.search(r"\w{3}\s\d{1,2},\s\d{4}", entrytext)]
                entrydate.append(
                    [
                        subresult.group(0).strip() if subresult else ""
                        for subresult in date_search
                    ][0]
                )  # pulls match text if match object is not none
            except Exception:
                entrydate.append("")

            try:
                pitches_search = [
                    re.search(r"·([^.]+\s(pitches))", entrytext)
                ]  # regex for starting at · and ending at first period only if it includes the word "pitches"
                pitchesinterm = [
                    subresult.group(0) if subresult else ""
                    for subresult in pitches_search
                ]
                pitches.append(
                    [
                        int(re.search(r"\d+", subresult).group(0).strip())
                        if subresult
                        else 1
                        for subresult in pitchesinterm
                    ][0]
                )  # take just the digit of the string
            except Exception:
                pitches.append(1)

            try:
                style_search = [
                    re.search(r"(Solo|TR|Follow|Lead|Send|Attempt|Flash)", entrytext)
                ]
                style_val = [
                    subresult.group(0).strip() if subresult else ""
                    for subresult in style_search
                ][
                    0
                ]  # I have a conditional in the comment search that depends on this so I made it a separate variable
                style.append(style_val)
            except Exception:
                style.append("")

            try:
                if style_val != "":
                    lead_style_search = [re.search(r"/([^.]+)", entrytext)]
                    lead_style.append(
                        [
                            subresult.group(0)[2:].strip() if subresult else ""
                            for subresult in lead_style_search
                        ][0]
                    )
                else:
                    lead_style.append("")
            except Exception:
                lead_style.append("")

            try:
                if style_val != "":
                    comment_search = [re.search(r"(Solo|TR|Follow|Lead).*", entrytext)]
                    commentinterm = [
                        subresult.group(0) if subresult else ""
                        for subresult in comment_search
                    ]
                    comment.append(
                        [
                            re.search(r"\..*", subresult).group(0)[2:].strip()
                            if subresult
                            else ""
                            for subresult in commentinterm
                        ][0]
                    )
                else:
                    comment_search = [
                        re.search(r"·(.*)", entrytext)
                    ]  # If no style comment then entire phrase is the comment.
                    comment.append(
                        [
                            subresult.group(0)[2:].strip() if subresult else ""
                            for subresult in comment_search
                        ][0]
                    )
            except Exception:
                comment.append("")
    print(
        len(name),
        len(namelink),
        len(entrydate),
        len(pitches),
        len(style),
        len(lead_style),
        len(comment),
    )
    print(name, namelink, entrydate, pitches, style, lead_style, comment)
