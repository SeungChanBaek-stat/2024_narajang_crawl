from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
import pandas as pd
import os
from datetime import datetime, timedelta


class SevenDays:
    def __init__(self, filename):
        self.today_date = datetime.now().strftime("%Y/%m/%d")
        
        # Define the base directory for file paths
        file_dir = "D:\\Dropbox\\#CRC_공유\\나라장터_\\"
        
        # Construct the full path to the crawling CSV file
        file_path = file_dir + f"crawling\\{filename}.csv"
        
        # Ensure the crawling folder exists
        if not os.path.exists(file_dir + "crawling"):
            os.makedirs(file_dir + "crawling")

        # Load the CSV file from the specified path
        self.df = pd.read_csv(file_path)
        self.filename = filename
    
    def transition(self):
        df = self.df
        df['공고일시'] = pd.to_datetime(df['공고일시'], errors='coerce').dt.strftime("%Y/%m/%d")
        df['마감일시'] = pd.to_datetime(df['마감일시'], errors='coerce').dt.strftime("%Y/%m/%d")

        seven_days_ago = (datetime.strptime(self.today_date, "%Y/%m/%d") - timedelta(days=7)).strftime("%Y/%m/%d")
        df = df.loc[df['공고일시'] >= seven_days_ago]

        # 새로운 엑셀 워크북 생성
        wb = Workbook()
        ws = wb.active

        # DataFrame을 엑셀 워크시트로 변환
        for r_idx, row in enumerate(dataframe_to_rows(df, index=False, header=True), 1):
            ws.append(row)
            # 각 행에 대해 열 너비와 정렬 설정
            if r_idx == 1:  # 헤더 행은 Bold로 설정 가능
                for cell in ws[r_idx]:
                    cell.alignment = Alignment(horizontal="center")

        # 열 너비 설정
        column_widths = {
            'A': 80,  # '제목' 열
            'B': 25,  # '수요기관' 열
            'C': 15,  # '공고일시' 열
            'D': 15   # '마감일시' 열
        }
        for col, width in column_widths.items():
            ws.column_dimensions[col].width = width
        # Ensure 'crawling' folder exists
        if not os.path.exists("crawling_7_days"):
            os.makedirs("crawling_7_days")

        # Set the target directory path
        target_dir = "D:\\Dropbox\\#CRC_공유\\나라장터_\\crawling_7_days"

        # Ensure the target 'crawling' folder exists
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 엑셀 파일로 저장
        wb.save(f"{target_dir}\\{self.filename}_1주치.xlsx")
        print(f"Data saved to {self.filename}_1주치.xlsx with specified column widths.")
