FROM python:3.8.10-slim

# 安裝 Chrome 和必要套件
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    unzip \
    chromium \
    chromium-driver

# 設定工作目錄
WORKDIR /app

# 複製需求文件
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY . .

# 設定環境變數
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:99

# 設定 Chrome 二進制檔案位置
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

CMD ["python", "src/getJob.py"]