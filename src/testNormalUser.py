from supabase import create_client

# 使用 normalUser 登入
supabase = create_client(
    "https://vijxlorrejpwltjnarfy.supabase.co",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZpanhsb3JyZWpwd2x0am5hcmZ5Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Mzk0NTI0ODcsImV4cCI6MjA1NTAyODQ4N30.JlWshs_HpOSRlL0u0ve1z2MGT4IrRsM9EE8znAblblA"
)

# 登入
response = supabase.auth.sign_in_with_password({
    "email": "normalUser1@gmail.com",
    "password": "0000"
})

# 測試讀取
response = supabase.table('jobs').select("*").limit(1).execute()
print("讀取測試結果：", response.data)

# 測試寫入（應該會失敗）
try:
    response = supabase.table('jobs').insert({
        "job_name": "test job"
    }).execute()
except Exception as e:
    print("預期中的錯誤：", e)