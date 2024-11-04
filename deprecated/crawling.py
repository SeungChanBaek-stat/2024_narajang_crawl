from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
from collections import OrderedDict
import pandas as pd

class CiCrawl:
    def __init__(self, website, accommodation_list):
        self.website = website
        self.accommdation_list = accommodation_list
        self.data = []  
        pass

    def initcrawl(self, x:str):
        '''
        params
        x : 검색단어
        '''
        driver = webdriver.Chrome()
        driver.get(self.website)
        # 페이지 로드 대기 (필요 시 조정)
        time.sleep(2)


        main = driver.window_handles
        print(main)

        # 아이프레임으로 전환 (필요 시)
        try:
            iframe = driver.find_element(By.TAG_NAME, 'iframe')
            driver.switch_to.frame(iframe)
        except:
            pass  # 아이프레임이 없으면 무시

        # 검색창 요소 기다리기 및 찾기
        search_input = WebDriverWait(driver, 5).until(
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

        main = driver.window_handles
        print(main)

        frames = driver.find_elements(By.TAG_NAME, 'frame')

        for frame in frames:
            frame_name = frame.get_attribute('name')
            print(f"프레임 이름 : {frame_name}")
        print(f"프레임 개수 : {len(frames)}")

        driver.switch_to.frame("sub")
        driver.execute_script("return window.frameElement.id;")
        time.sleep(5)



        # "입찰공고" 링크 클릭
        bid_notice_link = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a[href*=\"goCategory('TGONG')\"]"))
        )
        driver.execute_script("arguments[0].click();", bid_notice_link)

        main = driver.window_handles
        print(main)
        time.sleep(5)

        # "용역" 라디오 버튼 클릭
        service_radio_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'search_chk4'))
        )
        service_radio_button.click()

        main = driver.window_handles
        print(main)
        time.sleep(5)

        # "상세검색" 버튼 클릭
        detail_search_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//a[@class="btn_search" and text()="상세검색"]'))
        )
        detail_search_button.click()

        # "최근 1개월" 라디오 버튼 클릭
        date_radio_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, 'search_date1'))
        )
        date_radio_button.click()


        # "검색" 버튼 클릭
        search_submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@class="search" and @value="검색"]'))
        )
        search_submit_button.click()
        time.sleep(5)

        # Ensure search results are loaded
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "search_list"))
        )

        # Locate elements by class names and store them in lists
        titles = driver.find_elements(By.XPATH, '//strong[@class="tit"]/a')
        apparatus = driver.find_elements(By.XPATH, '//li[@class="m4"]/span')
        open_dates = driver.find_elements(By.XPATH, '//li[@class="m2"]/span')
        close_dates = driver.find_elements(By.XPATH, '//li[@class="m1"]/span')

        # Collect data in a structured format
        for i in range(len(titles)):
            try:
                title = titles[i].text
                apparatus_text = apparatus[i].text
                open_date = open_dates[i].text
                close_date = close_dates[i].text
                self.data.append({
                    "제목": title,
                    "수요기관": apparatus_text,
                    "공고일시": open_date,
                    "마감일시": close_date
                })
            except IndexError:
                print(f"Missing data for item {i + 1}")
                continue

        driver.quit()

        # Convert data to DataFrame
        df = pd.DataFrame(self.data)
        print(df)

        # Save DataFrame to CSV
        df.to_csv("crawling_results.csv", index=False, encoding="utf-8-sig")
        print("Data saved to crawling_results.csv")



accommodation_list = ["코비게스트하우스", "하이동대문한옥게스트하우스", "이지스테이임대"]


crawl_test = CiCrawl(website="https://www.g2b.go.kr/index.jsp",
                      accommodation_list = accommodation_list)

crawl_test.initcrawl(x = '도시재생')
