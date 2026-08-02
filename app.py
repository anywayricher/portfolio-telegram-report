import os
import requests
from telegram import Bot
from datetime import datetime
import asyncio
import time

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def send_telegram_message():
    """Telegram 메시지 발송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    message = """📊 포트폴리오 일일 리포트
📅 """ + datetime.now().strftime('%Y-%m-%d') + """

💰 현재 자산: 분석 필요
💵 현재 수익금: 분석 필요
📊 현재 수익률: 분석 필요

✅ 자동 배포 성공!"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print("✅ Telegram 메시지 발송 완료!")

async def main():
    while True:
        try:
            await send_telegram_message()
            print("메시지 발송 완료. 다음은 내일...")
        except Exception as e:
            print(f"오류: {e}")
        
        # 24시간 대기
        await asyncio.sleep(86400)

if __name__ == "__main__":
    asyncio.run(main())
