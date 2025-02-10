# AIOT x BIGDATA 職缺爬蟲

這個專案是一個自動化爬蟲系統，用於抓取 104 人力銀行中 AIOT 和 BIGDATA 相關的職缺資訊。

## 功能特點

- 自動抓取 104 人力銀行職缺資訊
- 支援多項職缺資訊爬取：
  - 基本資訊（職缺名稱、公司名稱等）
  - 工作內容與條件
  - 福利制度（法定福利、其他福利）
  - 聯絡方式
- 支援 Docker 容器化部署
- 跨平台支援（Windows、Mac、Linux）
- 自動保存資料為 CSV 格式

## 環境需求

- Python 3.8+
- Docker
- Git

## 安裝步驟

1. 複製專案
   ```bash
   git clone https://github.com/91910lin/AIOT-x-BIGDATA.git
   cd AIOT-x-BIGDATA
   ```

2. 使用 Docker 運行（推薦）
   ```bash
   docker-compose up --build
   ```

3. 本地運行（需要 Python 環境）
   ```bash
   pip install -r requirements.txt
   python src/getJob.py
   ```

## 專案結構

```bash
AIOT-x-BIGDATA/
├── src/
│ └── getJob.py # 主要爬蟲程式
├── Dockerfile # Docker 設定檔
├── docker-compose.yml # Docker Compose 設定檔
├── requirements.txt # Python 套件需求
└── README.md # 專案說明文件
```

## 輸出資料

爬取的資料會儲存在 `104_jobs.csv` 檔案中，包含以下資訊：
- 職缺基本資訊
  - 職缺名稱
  - 公司名稱
  - 更新日期
  - 工作地點
  - 薪資待遇
- 工作要求
  - 工作經驗
  - 學歷要求
  - 語言能力
  - 專業技能
- 福利制度
  - 法定福利
  - 其他福利
  - 詳細福利說明
- 聯絡資訊

## 使用說明

1. 程式會自動抓取 104 人力銀行的職缺資訊
2. 結果會儲存在 `104_jobs.csv` 檔案中
3. CSV 檔案包含職缺名稱、公司名稱、工作地點等資訊

## 注意事項

- 請遵守網站的使用規範
- 建議使用 Docker 環境運行，以確保環境一致性
- 如遇到問題，請檢查網路連線和 Docker 設定

## 授權

本專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 文件

## 作者

- [91910lin](https://github.com/91910lin)

## 更新紀錄

### 2025-02-11
- 新增福利制度爬取功能
- 新增聯絡方式爬取功能
- 優化 Docker 配置
- 改善程式碼結構
