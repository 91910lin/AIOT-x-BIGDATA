import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 設定 Selenium 選項
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# 根據環境設定 Chrome 路徑
if os.path.exists("/usr/bin/chromium"):  # Docker 環境
    chrome_options.binary_location = "/usr/bin/chromium"
    service = Service("/usr/bin/chromedriver")
else:  # Windows 本地環境
    service = Service(ChromeDriverManager().install())

driver = webdriver.Chrome(service=service, options=chrome_options)

# 設定目標 URL
search_keyword = "Python 工程師"
url = f"https://www.104.com.tw/jobs/search/?keyword={search_keyword}"
driver.get(url)
time.sleep(5)

# 定義目標元素的 CSS 選擇器
target_selector = 'div.job-summary'
max_scrolls = 2
scrolls = 0
job_list = []

while scrolls < max_scrolls:
    print(f"正在處理第 {scrolls + 1} 頁...")
    
    # 獲取當前頁面的職缺
    current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
    print(f"當前頁面職缺數量: {len(current_jobs)}")
    
    # 處理當前頁面的每個職缺
    for job in current_jobs:
        try:
            # 獲取職缺名稱和連結
            title_element = job.find_element(By.CSS_SELECTOR, 'h2 a.info-job__text')
            job_url = title_element.get_attribute('href')
            title = title_element.get_attribute('title')
            print("title:", title)
            print("job_url:", job_url)
            
            # 獲取公司名稱
            company = job.find_element(By.CSS_SELECTOR, 'a[data-gtm-joblist="職缺-公司名稱"]').text.strip()
            print("company:", company)
            
            # 開啟新分頁獲取詳細資訊
            driver.execute_script(f"window.open('{job_url}', '_blank')")
            driver.switch_to.window(driver.window_handles[-1])
            time.sleep(3)
            
            # 處理詳細頁面的資訊
            try:
                # 獲取更新日期，使用 title 屬性來獲取完整日期（包含年份）
                update_date_element = driver.find_element(By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')
                update_date = update_date_element.get_attribute('title')  # 獲取完整的 title 內容
                update_date = update_date.replace("更新", "").strip()  # 移除 "更新" 文字
                print("更新日期:", update_date)
                
                # 檢查是否為積極徵才中（可能不存在）
                try:
                    actively_hiring = driver.find_element(By.CSS_SELECTOR, 'div.actively-hiring-tag').text.strip()
                    actively_hiring = "是" if actively_hiring == "積極徵才中" else "否"
                except:
                    actively_hiring = "否"
                print("積極徵才:", actively_hiring)
                
                # 獲取應徵人數
                try:
                    applicants = driver.find_element(By.CSS_SELECTOR, 'a.d-flex.align-items-center.font-weight-bold').text.strip()
                    # 提取數字範圍（例如："應徵人數 0~5 人" -> "0~5"）
                    applicants = applicants.replace("應徵人數", "").replace("人", "").strip()
                    print("應徵人數:", applicants)
                except:
                    applicants = "無資料"
                    print("無法獲取應徵人數")
                
                # 更新要存入的資料
                job_list.append([title, company, update_date, actively_hiring, applicants])
                
            except Exception as e:
                print(f"處理詳細頁面資訊時發生錯誤: {e}")
                job_list.append([title, company, "", "否", "無資料"])  # 如果出錯，加入預設值
            
            # 關閉詳細頁面，切回列表頁
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
        except Exception as e:
            print(f"處理職缺時發生錯誤: {e}")
            continue
    
    # 滾動到下一頁
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 檢查是否有新職缺載入
    new_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
    if len(new_jobs) == len(current_jobs):
        print("沒有新的職缺載入，可能已到底部")
        break
        
    scrolls += 1

# 存入 CSV
df = pd.DataFrame(job_list, columns=["職缺名稱", "公司名稱", "更新日期", "積極徵才", "應徵人數"])
df.to_csv("104_jobs.csv", index=False, encoding="utf-8-sig")
print("爬取完成，已儲存為 104_jobs.csv")

driver.quit()