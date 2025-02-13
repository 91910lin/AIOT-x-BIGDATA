import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from supabase import create_client
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

# Supabase 設定
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase = create_client(
    "https://vijxlorrejpwltjnarfy.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpanhsb3JyZWpwd2x0am5hcmZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NTI0ODcsImV4cCI6MjA1NTAyODQ4N30.JlWshs_HpOSRlL0u0ve1z2MGT4IrRsM9EE8znAblblA"
)

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

# 搜尋關鍵字清單
keyword_list = [
    "iOS工程師", "Android工程師", "前端工程師", "後端工程師", "全端工程師",
    "數據分析師", "軟體工程師", "軟體助理工程師", "軟體專案主管", "系統分析師",
    "資料科學家", "資料工程師", "AI工程師", "演算法工程師", "韌體工程師",
    "電玩程式設計師", "Internet程式設計師", "資訊助理", "區塊鏈工程師", "BIOS工程師",
    "通訊軟體工程師", "電子商務技術主管", "其他資訊專業人員", "系統工程師",
    "網路管理工程師", "資安工程師", "資訊設備管制人員", "雲端工程師", "網路安全分析師",
    "MES工程師", "MIS程式設計師", "資料庫管理人員", "MIS/網管主管", "資安主管"
]

# 定義職缺區塊的 CSS 選擇器
target_selector = 'div.job-summary'
# 設定等待時間
WAIT_TIMEOUT = 10  # 最長等待10秒

# 讀取現有資料，如果沒有則建立空的 DataFrame（欄位與 CSV 欄位順序要一致）
def load_existing_jobs():
    try:
        response = supabase.table('jobs').select("*").execute()
        if len(response.data) > 0:
            existing_df = pd.DataFrame(response.data)
            return existing_df.set_index("job_url")
        return pd.DataFrame(columns=[
            "職缺名稱", "公司名稱", "公司網址", "更新日期", "積極徵才", "應徵人數",
            "工作內容", "職務類別", "工作待遇", "工作性質", "上班地點",
            "管理責任", "出差外派", "上班時段", "休假制度", "可上班日", "需求人數",
            "工作經歷", "學歷要求", "科系要求", "語文條件", "擅長工具", "工作技能",
            "具備證照", "其他條件", "法定福利", "其他福利", "未整理福利說明", "聯絡方式"
        ])
    except Exception as e:
        print(f"讀取 Supabase 資料時發生錯誤: {e}")
        return pd.DataFrame()

# 更新或新增職缺資料，同時更新 DataFrame 用於最後生成 CSV
def update_job_data(existing_df, new_data):
    try:
        job_url = new_data[0]
        job_record = {
            "job_url": job_url,
            "job_name": new_data[1],
            "company_name": new_data[2],
            "company_url": new_data[3],
            "update_date": new_data[4],
            "actively_hiring": new_data[5] == "是",
            "applicants": new_data[6],
            "job_description": new_data[7],
            "job_category": new_data[8],
            "salary": new_data[9],
            "job_type": new_data[10],
            "location": new_data[11],
            "management": new_data[12],
            "business_trip": new_data[13],
            "work_time": new_data[14],
            "vacation": new_data[15],
            "start_work": new_data[16],
            "headcount": new_data[17],
            "work_exp": new_data[18],
            "education": new_data[19],
            "major": new_data[20],
            "language": new_data[21],
            "tools": new_data[22],
            "skills": new_data[23],
            "certificates": new_data[24],
            "other_requirements": new_data[25],
            "legal_benefits": new_data[26],
            "other_benefits": new_data[27],
            "raw_benefits": new_data[28],
            "contact_info": new_data[29],
            "updated_at": datetime.now().isoformat()
        }

        # 檢查該職缺是否已存在
        existing_job = supabase.table('jobs').select("*").eq("job_url", job_url).execute()
        if len(existing_job.data) > 0:
            supabase.table('jobs').update(job_record).eq("job_url", job_url).execute()
            print(f"更新現有職缺: {job_url}")
        else:
            job_record["created_at"] = datetime.now().isoformat()
            supabase.table('jobs').insert(job_record).execute()
            print(f"新增職缺: {job_url}")
            
        # 更新 DataFrame
        new_df = pd.DataFrame([new_data[1:]], columns=existing_df.columns)
        new_df.index = [job_url]
        if job_url in existing_df.index:
            existing_df.loc[job_url] = new_df.loc[job_url]
        else:
            existing_df = pd.concat([existing_df, new_df])
            
        return existing_df
    except Exception as e:
        print(f"更新 Supabase 資料時發生錯誤: {e}")
        return existing_df

existing_jobs = load_existing_jobs()
job_count = 0
start_time = time.time()

# 針對每個搜尋關鍵字進行爬取
for search_keyword in keyword_list:
    print(f"\n正在搜尋關鍵字: {search_keyword}")
    url = f"https://www.104.com.tw/jobs/search/?keyword={search_keyword}"
    driver.get(url)
    time.sleep(5)  # 等待頁面初始載入

    old_scrolls = 0
    # 利用 while 迴圈持續滾動直到沒有新職缺載入
    while True:
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, target_selector))
            )
        except TimeoutException:
            print("等待職缺載入超時")
            break
        
        current_jobs = driver.find_elements(By.CSS_SELECTOR, target_selector)
        current_count = len(current_jobs)
        print(f"當前頁面職缺數量: {current_count}")

        # 處理尚未處理的新職缺
        for job in current_jobs[old_scrolls:]:
            job_start_time = time.time()
            try:
                job_count += 1
                print(f"\n處理第 {job_count} 筆職缺")
                print("-" * 50)
                
                # ※關鍵修正：從目前的職缺區塊內相對查找職缺標題與網址
                title_element = job.find_element(By.XPATH, './/h2//a[contains(@class, "info-job__text")]')
                job_url = title_element.get_attribute('href')
                job_name = title_element.get_attribute('title')
                print("職缺名稱:", job_name)
                print("職缺網址:", job_url)
                
                # 獲取公司資訊
                company_element = job.find_element(By.CSS_SELECTOR, 'a[data-gtm-joblist="職缺-公司名稱"]')
                company = company_element.text.strip()
                company_url = company_element.get_attribute('href')
                print("公司名稱:", company)
                print("公司網址:", company_url)
                
                # 開啟新分頁取得詳細資訊
                driver.execute_script(f"window.open('{job_url}', '_blank')")
                driver.switch_to.window(driver.window_handles[-1])
                
                WebDriverWait(driver, WAIT_TIMEOUT).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'p.job-description__content'))
                )
                
                # 處理詳細頁面的資訊
                try:
                    update_date_element = driver.find_element(By.CSS_SELECTOR, 'span.text-gray-darker[title*="更新"]')
                    update_date = update_date_element.get_attribute('title').replace("更新", "").strip()
                    print("更新日期:", update_date)
                    
                    try:
                        actively_hiring = driver.find_element(By.CSS_SELECTOR, 'div.actively-hiring-tag').text.strip()
                        actively_hiring = "是" if actively_hiring == "積極徵才中" else "否"
                    except:
                        actively_hiring = "否"
                    print("積極徵才:", actively_hiring)
                    
                    try:
                        applicants = driver.find_element(By.CSS_SELECTOR, 'a.d-flex.align-items-center.font-weight-bold').text.strip()
                        applicants = applicants.replace("應徵人數", "").replace("人", "").strip()
                        print("應徵人數:", applicants)
                    except:
                        applicants = "無資料"
                        print("無法獲取應徵人數")
                    
                    job_description = driver.find_element(By.CSS_SELECTOR, 'p.job-description__content').text.strip()
                    print("工作內容:", job_description)
                    
                    job_categories = driver.find_elements(By.CSS_SELECTOR, 'div.category-item u')
                    job_category = '、'.join([cat.text for cat in job_categories])
                    print("職務類別:", job_category)
                    
                    salary = driver.find_element(By.CSS_SELECTOR, 'p.text-primary.font-weight-bold').text.strip()
                    print("工作待遇:", salary)
                    
                    job_type = driver.find_element(By.CSS_SELECTOR, 'div.list-row:nth-child(4) div.list-row__data').text.strip()
                    print("工作性質:", job_type)
                    
                    location = driver.find_element(By.CSS_SELECTOR, 'div.job-address span').text.strip()
                    print("上班地點:", location)
                    
                    management_elements = driver.find_elements(By.CSS_SELECTOR, 'div.list-row')
                    def extract_info(target_title):
                        for element in management_elements:
                            try:
                                title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                                if title_text == target_title:
                                    return element.find_element(By.CSS_SELECTOR, 'div.list-row__data').text.strip()
                            except:
                                continue
                        return ""
                    management = extract_info("管理責任")
                    print("管理責任:", management)
                    
                    business_trip = extract_info("出差外派")
                    print("出差外派:", business_trip)
                    
                    work_time = extract_info("上班時段")
                    print("上班時段:", work_time)
                    
                    vacation = extract_info("休假制度")
                    print("休假制度:", vacation)
                    
                    start_work = extract_info("可上班日")
                    print("可上班日:", start_work)
                    
                    headcount = extract_info("需求人數")
                    print("需求人數:", headcount)
                    
                    work_exp = extract_info("工作經歷")
                    print("工作經歷:", work_exp)
                    
                    education = extract_info("學歷要求")
                    print("學歷要求:", education)
                    
                    major = extract_info("科系要求")
                    print("科系要求:", major)
                    
                    language = extract_info("語文條件")
                    print("語文條件:", language)
                    
                    def extract_list_info(target_title):
                        for element in management_elements:
                            try:
                                title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                                if title_text == target_title:
                                    items = element.find_elements(By.CSS_SELECTOR, 'div.list-row__data u')
                                    return '、'.join([item.text for item in items])
                            except:
                                continue
                        return ""
                    tools = extract_list_info("擅長工具")
                    print("擅長工具:", tools)
                    
                    skills = extract_list_info("工作技能")
                    print("工作技能:", skills)
                    
                    certificates = extract_list_info("具備證照")
                    print("具備證照:", certificates)
                    
                    other_requirements = ""
                    for element in management_elements:
                        try:
                            title_text = element.find_element(By.CSS_SELECTOR, 'h3').text.strip()
                            if title_text == "其他條件":
                                other_requirements = element.find_element(By.CSS_SELECTOR, 'div.list-row__data p.r3').text.strip()
                                break
                        except:
                            continue
                    print("其他條件:", other_requirements)
                    
                    try:
                        legal_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(3) span.tag--text a')
                        legal_benefits_str = '、'.join([item.text.strip() for item in legal_elements])
                        print("法定項目:", legal_benefits_str)
                        
                        other_elements = driver.find_elements(By.CSS_SELECTOR, 'div.benefits-labels:nth-child(5) span.tag--text a')
                        other_benefits_str = '、'.join([item.text.strip() for item in other_elements])
                        print("其他福利:", other_benefits_str)
                        
                        raw_benefits = driver.find_element(By.CSS_SELECTOR, 'div.benefits-description p.r3').text.strip()
                        print("未整理的福利說明:", raw_benefits)
                    except Exception as e:
                        print(f"獲取福利制度時發生錯誤: {e}")
                        legal_benefits_str = ""
                        other_benefits_str = ""
                        raw_benefits = ""
                    
                    try:
                        contact_elements = driver.find_elements(By.CSS_SELECTOR, 'div.job-contact-table div.job-contact-table__data')
                        contact_info_str = '\n'.join([element.text.strip() for element in contact_elements])
                        print("聯絡方式:", contact_info_str)
                    except Exception as e:
                        print(f"獲取聯絡方式時發生錯誤: {e}")
                        contact_info_str = ""
                    
                    # 準備儲存的資料（第一欄為 job_url，不會放入 CSV 中，而是作為 index）
                    job_data = [
                        job_url,
                        job_name, company, company_url, update_date, actively_hiring, applicants,
                        job_description, job_category, salary, job_type, location,
                        management, business_trip, work_time, vacation, start_work, headcount,
                        work_exp, education, major, language, tools, skills, certificates, 
                        other_requirements, legal_benefits_str, other_benefits_str, raw_benefits,
                        contact_info_str
                    ]
                    
                    existing_jobs = update_job_data(existing_jobs, job_data)
                    
                except Exception as e:
                    print(f"處理詳細頁面資訊時發生錯誤: {e}")
                
                driver.close()
                driver.switch_to.window(driver.window_handles[0])
                
                job_end_time = time.time()
                print(f"處理時間: {job_end_time - job_start_time:.2f} 秒")
                
            except Exception as e:
                print(f"處理職缺時發生錯誤: {e}")
                if len(driver.window_handles) > 1:
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                continue

        old_scrolls = current_count
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        
        try:
            WebDriverWait(driver, WAIT_TIMEOUT).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, target_selector)) > current_count
            )
        except TimeoutException:
            print("沒有新的職缺載入，可能已到底部")
            break

# 儲存 CSV（先把 index 轉回欄位，並更名為「職缺網址」）
try:
    final_df = existing_jobs.reset_index()
    final_df.columns.values[0] = "職缺網址"
    final_df.to_csv("104_jobs.csv", index=False, encoding="utf-8-sig")
    print("資料已更新至 Supabase 並儲存至 104_jobs.csv")
except Exception as e:
    print(f"儲存資料時發生錯誤: {e}")

end_time = time.time()
total_duration = end_time - start_time
hours = int(total_duration // 3600)
minutes = int((total_duration % 3600) // 60)
seconds = int(total_duration % 60)
print(f"\n總執行時間: {hours}小時 {minutes}分鐘 {seconds}秒")
print(f"總處理職缺數: {job_count} 筆")

driver.quit() 
