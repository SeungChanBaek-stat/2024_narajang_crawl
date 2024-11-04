from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from collections import OrderedDict
import pandas as pd
import re
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import math
from datetime import datetime
import os

class NaraCrawl:
    def __init__(self, website):
        self.website = website
        self.items = None
        self.data = []
        self.driver = webdriver.Chrome()   
        pass

    def init_crawl(self, x:str):
        '''
        params
        x : 검색단어
        '''
        self.x = x
        driver = self.driver
        driver.get(self.website)

        # 아이프레임으로 전환 (필요 시)
        try:
            iframe = driver.find_element(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(iframe)
        except:
            pass  # 아이프레임이 없으면 무시

        # 검색창 요소 기다리기 및 찾기
        search_input = WebDriverWait(driver, 2).until(
            EC.presence_of_element_located((By.XPATH, '//input[@name="keyword"]'))
        )

        # 검색단어 입력
        search_input.send_keys(x)

        # 검색 버튼 요소 기다리기 및 클릭
        search_button = driver.find_element(By.XPATH, '//img[@alt="검색"]/parent::a')
        search_button.click()

        main = driver.window_handles
        print(main)

        for i in main:
            if i != main[0]:
                driver.switch_to.window(i)
                driver.close()

        driver.switch_to.window(main[0])

        frames = driver.find_elements(By.TAG_NAME, 'frame')


        driver.switch_to.frame("sub")
        driver.execute_script("return window.frameElement.id;")



        # "입찰공고" 링크 클릭
        bid_notice_link = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*=\"goCategory('TGONG')\"]"))
        )
        driver.execute_script("arguments[0].click();", bid_notice_link)


        # "용역" 라디오 버튼 클릭
        service_radio_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, 'search_chk4'))
        )
        service_radio_button.click()


        # "상세검색" 버튼 클릭
        detail_search_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="btn_search" and text()="상세검색"]'))
        )
        detail_search_button.click()

        # "최근 1개월" 라디오 버튼 클릭
        date_radio_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.ID, 'search_date1'))
        )
        date_radio_button.click()


        # "검색" 버튼 클릭
        search_submit_button = WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@class="search" and @value="검색"]'))
        )
        search_submit_button.click()

    def crawl_by_page(self, progress_bar=None, status_text=None):
        driver = self.driver

        # Ensure search results are loaded
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search_list"))
        )

        # Extract total number of results
        total_results_text = driver.find_element(By.XPATH, '//div[@class="tit_bar"]/h3').text
        print(total_results_text)
        total_results_text = total_results_text.replace(",", "")
        print(total_results_text)
        match = re.search(r'(\d+)\s*건', total_results_text)
        total_results = int(match.group(1))
        # total_results = int(re.search(r'\((\d+)건\)', total_results_text).group(1))

        # Calculate total number of pages (10 results per page)
        total_pages = math.ceil(total_results / 10)
        self.total_pages = total_pages
        print(f"Total results: {total_results}, Total pages: {total_pages}")

        self.current_page = 1
        while self.current_page <= total_pages:
            print(f"Processing page {self.current_page}/{total_pages}")

            # Wait for items to load
            WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "search_list"))
            )

            # Collect items on the current page
            self.items = driver.find_elements(By.XPATH, '//ul[@class="search_list"]/li')
            self.index_and_collect_data()

            # Update progress bar if provided
            if progress_bar and status_text:
                progress = self.current_page / total_pages
                progress_bar.progress(progress)
                progress_percentage = progress * 100
                status_text.text(f"현재 {progress_percentage:.2f} 크롤링 완료했습니다.")

            # Break if we've reached the last page
            if self.current_page >= total_pages:
                break

            # Navigate to the next page
            self.current_page += 1
            self.goto_page(self.current_page)

        driver.quit()

        # Convert data to DataFrame
        df = pd.DataFrame(self.data)
        print(df)

        # Ensure 'crawling' folder exists
        if not os.path.exists("crawling"):
            os.makedirs("crawling")

        # Set the target directory path
        target_dir = "D:\\Dropbox\\#CRC_공유\\나라장터_\\crawling"

        # Ensure the target 'crawling' folder exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)


        # Save DataFrame to CSV in the 'crawling' folder
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        df.to_csv(f"{target_dir}\\{self.x}_크롤링_{formatted_date}.csv", index=False, encoding="utf-8-sig")
        print("Data saved to crawling folder.")

    def goto_page(self, page_number):
        driver = self.driver

        # Find the pagination element
        try:
            pagination = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.CLASS_NAME, "page"))
            )
        except TimeoutException:
            print("Pagination not found")
            return

        # Calculate the group of pages (e.g., 1-10, 11-20)
        page_group = ((page_number - 1) // 10) * 10

        # If we're at the start of a new page group, click the "Next" button
        if page_number % 10 == 1 and page_number != 1:
            try:
                next_button = driver.find_element(By.CLASS_NAME, "page_next")
                driver.execute_script("arguments[0].click();", next_button)
                time.sleep(2)  # Wait for the page to load
            except NoSuchElementException:
                print("Next button not found")
                return

        # Click on the page number
        try:
            page_link = driver.find_element(By.XPATH, f'//span[@class="page"]/a[text()="{page_number}"]')
            driver.execute_script("arguments[0].click();", page_link)
            time.sleep(2)  # Wait for the page to load
        except NoSuchElementException:
            print(f"Page number {page_number} not found")
            return

    def index_and_collect_data(self):
        for index, item in enumerate(self.items):
            try:
                # Extract title
                try:
                    title_element = item.find_element(By.XPATH, './/strong[@class="tit"]/a')
                    title = title_element.text
                except NoSuchElementException:
                    title = "-"

                # Extract apparatus
                try:
                    apparatus_element = item.find_element(By.XPATH, './/li[@class="m4"]/span')
                    apparatus_text = apparatus_element.text
                except NoSuchElementException:
                    apparatus_text = "-"

                # Extract open date
                try:
                    open_date_element = item.find_element(By.XPATH, './/li[@class="m2"]/span')
                    open_date = open_date_element.text
                except NoSuchElementException:
                    open_date = "-"

                # Extract close date
                try:
                    close_date_element = item.find_element(By.XPATH, './/li[@class="m1"]/span')
                    close_date = close_date_element.text
                except NoSuchElementException:
                    close_date = "-"

                self.data.append({
                    "제목": title,
                    "수요기관": apparatus_text,
                    "공고일시": open_date,
                    "마감일시": close_date
                })
            except Exception as e:
                print(f"Error processing item {index + 1}: {e}")
                continue