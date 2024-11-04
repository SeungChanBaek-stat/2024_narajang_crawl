import streamlit as st
from functions import NaraCrawl, SevenDays
from datetime import datetime
import time

def run_crawl(search_keyword):
    try:
        crawl_start_time = time.time()
        crawl_test = NaraCrawl.NaraCrawl(website="https://www.g2b.go.kr/index.jsp")
        crawl_test.init_crawl(x=search_keyword)

        # total_pages = crawl_test.total_pages

        progress_bar = st.progress(0)
        status_text = st.empty()

        crawl_test.crawl_by_page(progress_bar=progress_bar, status_text=status_text)

        # Calculate and display crawl duration
        crawl_duration = time.time() - crawl_start_time
        st.success(f"{search_keyword} 크롤링 완료 (걸린 시간: {crawl_duration:.2f}초)")

    except Exception as e:
        st.error(f"오류가 발생하였습니다: {e}")

def run_sort(filename):
    try:
        # Start timing the sorting
        sort_start_time = time.time()

        sevendays = SevenDays.SevenDays(filename)
        sevendays.transition()

        # Calculate and display sorting duration
        sort_duration = time.time() - sort_start_time
        st.success(f"{filename} 1주일 이하로 정렬 완료 (걸린 시간: {sort_duration:.2f}초)")
    except Exception as e:
        st.error(f"오류가 발생하였습니다: {e}")
# Streamlit UI
st.title("나라장터 크롤링_v2")

search_keyword = st.text_input("검색하려는 단어를 입력하세요:", "")

if st.button("Start Crawling"):
    if search_keyword:
        now = datetime.now()
        formatted_date = now.strftime("%Y-%m-%d")
        filename = f"{search_keyword}_크롤링_{formatted_date}"
        st.info(f"{search_keyword} 크롤링중입니다.")
        run_crawl(search_keyword)
        st.info(f"오늘날짜 {formatted_date} 기준 1주일이하로 정렬중입니다.")
        run_sort(filename)

    else:
        st.warning("단어를 입력하세요.")
