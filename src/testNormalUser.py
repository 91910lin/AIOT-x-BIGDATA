import os
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# 檢查環境變數
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_ANON_KEY')

print("檢查環境變數:")
print(f"SUPABASE_URL: {supabase_url}")
print(f"SUPABASE_KEY: {supabase_key}")

# 初始化 Supabase 客戶端
supabase = create_client(supabase_url, supabase_key)

try:
    # 先嘗試登入
    print("\n嘗試登入...")
    auth_response = supabase.auth.sign_in_with_password({
        "email": "normaluser@gmail.com",
        # "email": "no@test.com",
        "password": "0000"
    })
    print("登入成功：", auth_response)

    # 等待一下確保登入狀態已更新
    import time
    time.sleep(1)

    # 嘗試讀取資料
    print("\n嘗試讀取資料...")
    data = supabase.table('jobs').select("*").limit(1).execute()
    print("讀取成功：", data.data)

    # 測試寫入（應該會失敗）
    try:
        response = supabase.table('jobs').insert({
            "job_name": "test job"
        }).execute()
    except Exception as e:
        print("預期中的錯誤：", e)

except Exception as e:
    print(f"\n錯誤類型: {type(e)}")
    print(f"錯誤訊息: {str(e)}")
    import traceback
    print("\n詳細錯誤:")
    print(traceback.format_exc())