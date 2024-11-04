from functions import NaraCrawl

if __name__ == "__main__":
    # Prompt user to input the search keyword
    search_keyword = input("검색하려는 단어를 입력하세요 : ")

    # Initialize and start crawling with the entered keyword
    crawl_test = NaraCrawl.NaraCrawl(website="https://www.g2b.go.kr/index.jsp")
    crawl_test.init_crawl(x=search_keyword)
    crawl_test.crawl_by_page()