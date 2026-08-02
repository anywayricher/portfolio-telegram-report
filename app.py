import os
import requests
from telegram import Bot
from datetime import datetime
import asyncio

# 환경 변수에서 토큰과 Chat ID 읽기
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

스크린샷을 업로드해주세요!"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print("✅ Telegram 메시지 발송 완료!")

if __name__ == "__main__":
    asyncio.run(send_telegram_message())
