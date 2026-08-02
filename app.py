import os
import requests
from telegram import Bot
import asyncio

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

async def test_api():
    """영웅문 API 테스트"""
    try:
        # 키움 REST API 테스트
        url = "https://openapi.kiwoom.com:9443/oauth2/authorization/access_token"
        response = requests.get(url, timeout=5)
        print(f"✅ API 연결 성공: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ API 연결 실패: {e}")
        return False

async def send_result(success):
    """결과를 Telegram으로 발송"""
    bot = Bot(token=TELEGRAM_TOKEN)
    
    if success:
        message = "✅ Render에서 영웅문 API 연결 성공!"
    else:
        message = "❌ Render에서 영웅문 API 포트 9443 차단됨"
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

async def main():
    result = await test_api()
    await send_result(result)

if __name__ == "__main__":
    asyncio.run(main())
