import os
import asyncio
import threading
import time
from datetime import datetime
from flask import Flask
from telegram import Bot
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 고정 포트폴리오 데이터
PORTFOLIO = {
    'SK하이닉스': {'수량': 50, '평단가': 2870340, '계좌': '메리츠'},
    '삼성전자': {'수량': 347, '평단가': 351751, '계좌': '메리츠'},
    '서진시스템': {'수량': 1, '평단가': 57800, '계좌': '메리츠'},
    'KODEX S&P500': {'수량': 2354, '평단가': 25485, '계좌': '미래'},
    'KODEX 나스닥100': {'수량': 2062, '평단가': 29090, '계좌': '미래'},
    'KODEX AI반도체TOP': {'수량': 2465, '평단가': 52163, '계좌': '미래'},
}

ACCOUNT_INFO = {
    '메리츠': {'원금': 14100, '현금': 0},
    '미래': {'원금': 20000, '현금': 8606}
}

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

def get_current_prices():
    """테스트용 임시 현재가"""
    print("[DEBUG] 현재가 수집 시작...")
    
    try:
        # 테스트: 고정 가격으로 테스트
        prices = {
            'SK하이닉스': 1718000,
            '삼성전자': 262500,
            '서진시스템': 33000,
            'KODEX S&P500': 25485,
            'KODEX 나스닥100': 29090,
            'KODEX AI반도체TOP': 52163,
        }
        
        print(f"[DEBUG] ✅ 현재가 수집 성공: {prices}")
        return True, prices
        
    except Exception as e:
        print(f"[DEBUG] ❌ 현재가 수집 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def calculate_portfolio(prices):
    """포트폴리오 계산"""
    print("[DEBUG] 포트폴리오 계산 시작...")
    
    meritz_total = 0
    future_total = 0
    meritz_profit = 0
    future_profit = 0
    
    for ticker, data in PORTFOLIO.items():
        if ticker in prices:
            current_price = prices[ticker]
            quantity = data['수량']
            avg_price = data['평단가']
            account = data['계좌']
            
            eval_amount = current_price * quantity
            profit = eval_amount - (avg_price * quantity)
            
            if account == '메리츠':
                meritz_total += eval_amount
                meritz_profit += profit
            else:
                future_total += eval_amount
                future_profit += profit
    
    print(f"[DEBUG] ✅ 계산 완료 - 메리츠: {meritz_total}, 미래: {future_total}")
    
    return {
        'meritz_total': meritz_total,
        'future_total': future_total,
        'meritz_profit': meritz_profit,
        'future_profit': future_profit
    }

async def send_report(prices, calc):
    """일일 리포트 생성 및 발송"""
    print("[DEBUG] 리포트 생성 시작...")
    
    bot = Bot(token=TELEGRAM_TOKEN)
    
    total_asset = calc['meritz_total'] + calc['future_total'] + ACCOUNT_INFO['미래']['현금']
    total_profit = calc['meritz_profit'] + calc['future_profit']
    total_return = (total_profit / (ACCOUNT_INFO['메리츠']['원금'] + ACCOUNT_INFO['미래']['원금'])) * 100
    
    report = f"""📊 포트폴리오 일일 리포트
📅 {datetime.now().strftime('%Y-%m-%d')}

💰 현재 자산: {total_asset/10000:.0f}만원
💵 현재 수익금: +{total_profit/10000:.0f}만원
📊 현재 수익률: +{total_return:.1f}%

🏦 메리츠증권: {calc['meritz_total']/10000:.0f}만원
   • 원금: 14,100만원
   • 수익금: +{calc['meritz_profit']/10000:.0f}만원

🏦 미래에셋증권: {(calc['future_total'] + ACCOUNT_INFO['미래']['현금'])/10000:.0f}만원
   • 원금: 20,000만원
   • 수익금: +{calc['future_profit']/10000:.0f}만원
   • 현금: 8,606만원"""
    
    print(f"[DEBUG] Telegram 발송 시작... Token: {TELEGRAM_TOKEN[:20]}...")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report)
    print("✅ 리포트 발송 완료!")

def background_task():
    """백그라운드 작업"""
    print("[DEBUG] 백그라운드 작업 시작!")
    
    try:
        success, prices = get_current_prices()
        if success:
            calc = calculate_portfolio(prices)
            asyncio.run(send_report(prices, calc))
        else:
            print("[DEBUG] 현재가 수집 실패")
    except Exception as e:
        print(f"[DEBUG] ❌ 백그라운드 작업 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("[DEBUG] Flask 시작 전 - 백그라운드 스레드 실행")
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    print("[DEBUG] 백그라운드 스레드 생성됨, 2초 대기...")
    time.sleep(2)
    
    port = int(os.getenv('PORT', 5000))
    print(f"[DEBUG] Flask 서버 시작 - 포트: {port}")
    app.run(host='0.0.0.0', port=port)
