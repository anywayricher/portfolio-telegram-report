import os
import requests
from telegram import Bot
from datetime import datetime
import asyncio
import threading
import time
from flask import Flask

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
KIWOOM_APP_KEY = os.getenv('KIWOOM_APP_KEY')
KIWOOM_APP_SECRET = os.getenv('KIWOOM_APP_SECRET')

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

async def test_kiwoom_api():
    """키움 REST API 테스트"""
    try:
        # 키움 API 접속 테스트
        url = "https://openapi.kiwoom.com:9443/oauth2/authorization/access_token"
        headers = {
            'content-type': 'application/json',
        }
        params = {
            'grant_type': 'authorization_code',
            'appkey': KIWOOM_APP_KEY,
            'appsecret': KIWOOM_APP_SECRET,
            'code': 'test'
        }
        
        response = requests.post(url, headers=headers, params=params, timeout=5)
        print(f"✅ API 접속 성공: {response.status_code}")
        return True, f"성공: {response.status_code}"
    except Exception as e:
        print(f"❌ API 접속 실패: {e}")
        return False, f"실패: {str(e)}"

async def send_result(success, message):
    bot = Bot(token=TELEGRAM_TOKEN)
    
    if success:
        text = f"""✅ Render에서 키움 API 포트 9443 접속 가능!
{message}"""
    else:
        text = f"""❌ Render에서 키움 API 포트 9443 차단됨
{message}"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=text)

def background_task():
    """백그라운드 작업"""
    try:
        result, message = asyncio.run(test_kiwoom_api())
        asyncio.run(send_result(result, message))
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    # 백그라운드에서 API 테스트 실행
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    
    # Flask 앱 실행
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
