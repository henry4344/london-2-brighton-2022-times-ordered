import requests
from bs4 import BeautifulSoup
import pandas as pd
import time

from selenium import webdriver
from selenium.webdriver.chrome.service import Service


def get_last_table_page_num(soup):
    table = soup.find("table", id="ctl00_Content_Main_grdTopPager")

    for j in table.find_all("tr"):
        row_data = j.find_all("td")
        for num, row in enumerate(row_data):

            link = row.find("a")

            if num == len(row_data) - 1:
                return int(link.text)


def main():
    url = "https://results.racetimingsolutions.co.uk/results.aspx?CId=16269&RId=1518"

    page = requests.get(url)

    soup = BeautifulSoup(page.text, "lxml")

    last_page = get_last_table_page_num(soup)

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("start-maximized")

    service_obj = Service(r".\chromedriver.exe")
    driver = webdriver.Chrome(service=service_obj)
    driver.get("https://results.racetimingsolutions.co.uk/results.aspx?CId=16269&RId=1518")

    headers = ["Race No", "Name", "Time"]
    col_list = [1, 2, 4]
    all_data_frames = []

    for page in range(1, last_page):

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        table1 = soup.find(
            "table",
            {
                "class": "table table-striped table-bordered xtable-responsive table-sm xtable-hover small align-middle ltw-cell-center"
            },
        )

        # Create a dataframe
        page_data = pd.DataFrame(columns=headers)

        for j in table1.find_all("tr")[1:]:
            row_data = j.find_all("td")
            row = [i.text for index, i in enumerate(row_data) if index in col_list]
            length = len(page_data)
            page_data.loc[length] = row

        all_data_frames.append(page_data)

        # go to next page
        driver.find_element("link text", f"{page+1}").click()

    all_data = pd.concat(all_data_frames)

    # all_data["Time"] = pd.to_datetime(all_data["Time"], format="%H:%M:%S").dt.time
    all_data = all_data.sort_values("Time")

    all_data.to_csv("./all_riders_time_ordered.csv")

    driver.quit()


if __name__ == "__main__":
    start_time = time.time()

    main()

    total_time = time.time() - start_time
    print(f"Time taken: {total_time}s")
