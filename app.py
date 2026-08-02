import os
import asyncio
import threading
import time
from flask import Flask
from telegram import Bot
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

def scrape_kiwoom_data():
    """영웅문 웹사이트에서 포트폴리오 데이터 수집"""
    try:
        # Selenium으로 브라우저 열기
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # 백그라운드 실행
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        
        driver = webdriver.Chrome(options=options)
        
        # 영웅문 로그인 페이지
        driver.get("https://www.kiwoom.com/h/stock/account")
        
        # 페이지 로딩 대기
        time.sleep(3)
        
        # 페이지 HTML 파싱
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        driver.quit()
        
        print("✅ 영웅문 데이터 수집 성공!")
        return True, "데이터 수집 완료"
        
    except Exception as e:
        print(f"❌ 데이터 수집 실패: {e}")
        return False, f"오류: {str(e)}"

async def send_result(success, message):
    """Telegram으로 결과 발송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    if success:
        text = f"""✅ 영웅문 웹 스크래핑 성공!
{message}"""
    else:
        text = f"""❌ 영웅문 웹 스크래핑 실패
{message}"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

def background_task():
    """백그라운드 작업"""
    try:
        success, message = scrape_kiwoom_data()
        asyncio.run(send_result(success, message))
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    # 백그라운드에서 웹 스크래핑 실행
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    
    # Flask 앱 실행
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
