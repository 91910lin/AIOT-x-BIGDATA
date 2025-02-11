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
max_scrolls = 1
scrolls = 0
job_list = []

# 檢查是否存在舊的 CSV 檔案並讀取
def load_existing_jobs():
    try:
        if os.path.exists("104_jobs.csv"):
            existing_df = pd.read_csv("104_jobs.csv", encoding="utf-8-sig")
            # 將職缺網址作為索引
            return existing_df.set_index("職缺網址")
        # 如果檔案不存在，建立一個有正確欄位的空 DataFrame
        return pd.DataFrame(columns=[
            "職缺名稱", "公司名稱", "公司網址", "更新日期", "積極徵才", "應徵人數",
            "工作內容", "職務類別", "工作待遇", "工作性質", "上班地點",
            "管理責任", "出差外派", "上班時段", "休假制度", "可上班日", "需求人數",
            "工作經歷", "學歷要求", "科系要求", "語文條件", "擅長工具", "工作技能", "具備證照", 
            "其他條件", "法定福利", "其他福利", "未整理福利說明", "聯絡方式"
        ])
    except Exception as e:
        print(f"讀取現有 CSV 檔案時發生錯誤: {e}")
        return pd.DataFrame()

# 更新或新增職缺資料
def update_job_data(existing_df, new_data):
    try:
        # 將新資料轉換為 DataFrame
        new_df = pd.DataFrame([new_data[1:]], columns=existing_df.columns)
        new_df.index = [new_data[0]]  # 使用職缺網址作為索引
        
        # 如果職缺已存在，更新資料
        if new_data[0] in existing_df.index:
            existing_df.loc[new_data[0]] = new_df.loc[new_data[0]]
            print(f"更新現有職缺: {new_data[0]}")
        else:
            # 如果是新職缺，新增一筆
            existing_df = pd.concat([existing_df, new_df])
            print(f"新增職缺: {new_data[0]}")
            
        return existing_df
    except Exception as e:
        print(f"更新資料時發生錯誤: {e}")
        return existing_df

# 載入現有資料
existing_jobs = load_existing_jobs()

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
            job_name = title_element.get_attribute('title')
            print("職缺名稱:", job_name)
            print("職缺網址:", job_url)
            
            # 獲取公司名稱
            company_element = job.find_element(By.CSS_SELECTOR, 'a[data-gtm-joblist="職缺-公司名稱"]')
            company = company_element.text.strip()
            company_url = company_element.get_attribute('href')
            print("公司名稱:", company)
            print("公司網址:", company_url)
            
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
                
                # 獲取工作內容
                job_description = driver.find_element(By.CSS_SELECTOR, 'p.job-description__content').text.strip()
                print("工作內容:", job_description)
                
                # 獲取職務類別
                job_categories = driver.find_elements(By.CSS_SELECTOR, 'div.category-item u')
                job_category = '、'.join([cat.text for cat in job_categories])
                print("職務類別:", job_category)
                
                # 獲取工作待遇
                salary = driver.find_element(By.CSS_SELECTOR, 'p.text-primary.font-weight-bold').text.strip()
                print("工作待遇:", salary)
                
                # 獲取工作性質
                job_type = driver.find_element(By.CSS_SELECTOR, 'div.list-row:nth-child(4) div.list-row__data').text.strip()
                print("工作性質:", job_type)
                
                # 獲取上班地點
                location = driver.find_element(By.CSS_SELECTOR, 'div.job-address span').text.strip()
                print("上班地點:", location)
                
                # 獲取管理責任
                management_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                management = ""
                for element in management_elements:
                    try:
                        title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title_text == "管理責任":
                            management = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("管理責任:", management)
                
                # 獲取出差外派
                business_trip = ""
                for element in management_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "出差外派":
                            business_trip = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("出差外派:", business_trip)
                
                # 獲取上班時段
                work_time = ""
                for element in management_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "上班時段":
                            work_time = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("上班時段:", work_time)
                
                # 獲取休假制度
                vacation = ""
                for element in management_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "休假制度":
                            vacation = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("休假制度:", vacation)
                
                # 獲取可上班日
                start_work = ""
                for element in management_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "可上班日":
                            start_work = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("可上班日:", start_work)
                
                # 獲取需求人數
                headcount = ""
                for element in management_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "需求人數":
                            headcount = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("需求人數:", headcount)
                
                # 獲取工作經歷
                work_exp = ""
                work_exp_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "工作經歷":
                            work_exp = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("工作經歷:", work_exp)
                
                # 獲取學歷要求
                education = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "學歷要求":
                            education = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("學歷要求:", education)
                
                # 獲取科系要求
                major = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "科系要求":
                            major = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("科系要求:", major)
                
                # 獲取語文條件
                language = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "語文條件":
                            language = element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            break
                    except:
                        continue
                print("語文條件:", language)
                
                # 獲取擅長工具
                tools = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "擅長工具":
                            tools_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                            tools = '、'.join([tool.text for tool in tools_elements])
                            break
                    except:
                        continue
                print("擅長工具:", tools)
                
                # 獲取工作技能
                skills = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "工作技能":
                            skills_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                            skills = '、'.join([skill.text for skill in skills_elements])
                            break
                    except:
                        continue
                print("工作技能:", skills)
                
                # 獲取具備證照
                certificates = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "具備證照":
                            cert_elements = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                            certificates = '、'.join([cert.text for cert in cert_elements])
                            break
                    except:
                        continue
                print("具備證照:", certificates)
                
                # 獲取其他條件
                other_requirements = ""
                for element in work_exp_elements:
                    try:
                        title = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                        if title == "其他條件":
                            other_requirements = element.find_element(By.CSS_SELECTOR, 'div.list-row__data p.r3').text.strip()
                            break
                    except:
                        continue
                print("其他條件:", other_requirements)
                
                # 獲取福利制度
                try:
                    # 法定項目
                    legal_benefits = []
                    legal_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(3) span.tag--text a')
                    legal_benefits = [item.text.strip() for item in legal_elements]
                    legal_benefits_str = '、'.join(legal_benefits)
                    print("法定項目:", legal_benefits_str)
                    
                    # 其他福利
                    other_benefits = []
                    other_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(5) span.tag--text a')
                    other_benefits = [item.text.strip() for item in other_elements]
                    other_benefits_str = '、'.join(other_benefits)
                    print("其他福利:", other_benefits_str)
                    
                    # 未整理的福利說明
                    raw_benefits = ""
                    benefits_description = driver.find_element(By.CSS_SELECTOR, 'div.benefits-description p.r3').text.strip()
                    raw_benefits = benefits_description
                    print("未整理的福利說明:", raw_benefits)
                    
                except Exception as e:
                    print(f"獲取福利制度時發生錯誤: {e}")
                    legal_benefits_str = ""
                    other_benefits_str = ""
                    raw_benefits = ""
                
                # 獲取聯絡方式
                try:
                    contact_info = []
                    contact_elements = driver.find_elements(By.CSS_SELECTOR, 'div.job-contact-table div.job-contact-table__data')
                    contact_info = [element.text.strip() for element in contact_elements]
                    contact_info_str = '\n'.join(contact_info)
                    print("聯絡方式:", contact_info_str)
                except Exception as e:
                    print(f"獲取聯絡方式時發生錯誤: {e}")
                    contact_info_str = ""
                
                # 準備要儲存的資料
                job_data = [
                    job_url,  # 使用職缺網址作為索引
                    job_name, company, company_url, update_date, actively_hiring, applicants,
                    job_description, job_category, salary, job_type, location,
                    management, business_trip, work_time, vacation, start_work, headcount,
                    work_exp, education, major, language, tools, skills, certificates, 
                    other_requirements, legal_benefits_str, other_benefits_str, raw_benefits,
                    contact_info_str
                ]
                
                # 更新或新增資料
                existing_jobs = update_job_data(existing_jobs, job_data)
                
            except Exception as e:
                print(f"處理詳細頁面資訊時發生錯誤: {e}")
            
            # 關閉詳細頁面，切回列表頁
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
            
        except Exception as e:
            print(f"處理職缺時發生錯誤: {e}")
            continue

        # 獲取終端寬度並打印分隔線
        terminal_width = os.get_terminal_size().columns
        print("=" * terminal_width)
    
    # 滾動到下一頁
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)
    
    # 檢查是否有新職缺載入
    new_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
    if len(new_jobs) == len(current_jobs):
        print("沒有新的職缺載入，可能已到底部")
        break
        
    scrolls += 1

# 儲存更新後的資料
try:
    # 重設索引，將職缺網址變回一般欄位
    existing_jobs.reset_index().to_csv("104_jobs.csv", index=False, encoding="utf-8-sig")
    print("資料已更新並儲存至 104_jobs.csv")
except Exception as e:
    print(f"儲存 CSV 檔案時發生錯誤: {e}")

driver.quit()