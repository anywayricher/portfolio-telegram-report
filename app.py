import os
from flask import Flask
from telegram import Bot
from datetime import datetime
import asyncio
import threading
import time

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

async def send_telegram_message():
    """Telegram 메시지 발송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    message = """📊 포트폴리오 일일 리포트
📅 """ + datetime.now().strftime('%Y-%m-%d') + """

💰 현재 자산: 분석 필요
💵 현재 수익금: 분석 필요
📊 현재 수익률: 분석 필요

✅ Render 자동화 실행 중!"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print("✅ Telegram 메시지 발송 완료!")

def background_task():
    """백그라운드에서 24시간마다 실행"""
    while True:
        try:
            asyncio.run(send_telegram_message())
            print("메시지 발송 완료. 다음은 내일...")
        except Exception as e:
            print(f"오류: {e}")
        
        # 24시간 대기
        time.sleep(86400)

if __name__ == "__main__":
    # 백그라운드 스레드 시작
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    
    # Flask 앱 실행 (포트 5000)
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
