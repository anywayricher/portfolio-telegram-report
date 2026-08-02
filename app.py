import os
import asyncio
import threading
from flask import Flask
from telegram import Bot
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

def analyze_kiwoom_html():
    """영웅문 HTML 구조 분석"""
    try:
        url = "https://www.kiwoom.com/h/stock/account"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 전체 HTML 길이 확인
        html_length = len(response.text)
        
        # 자산, 수익금 관련 텍스트 찾기
        text = soup.get_text()
        
        # 주요 클래스/ID 찾기
        divs = soup.find_all('div', limit=20)
        classes = [div.get('class') for div in divs if div.get('class')]
        
        print(f"✅ HTML 분석 완료!")
        return True, f"HTML 길이: {html_length}자, 발견된 클래스: {len(set(str(c) for c in classes))}"
        
    except Exception as e:
        print(f"❌ HTML 분석 실패: {e}")
        return False, f"오류: {str(e)}"

async def send_result(success, message):
    bot = Bot(token=TELEGRAM_TOKEN)
    
    if success:
        text = f"""✅ 영웅문 HTML 분석 성공!
{message}"""
    else:
        text = f"""❌ 영웅문 HTML 분석 실패
{message}"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

def background_task():
    try:
        success, message = analyze_kiwoom_html()
        asyncio.run(send_result(success, message))
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
