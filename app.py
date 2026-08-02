import os
import asyncio
import threading
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
    """네이버 금융에서 현재가 수집"""
    prices = {}
    
    try:
        # SK하이닉스
        response = requests.get('https://finance.naver.com/item/main.naver?code=000660')
        soup = BeautifulSoup(response.content, 'html.parser')
        price = soup.find('span', {'class': 'blind'})
        if price:
            prices['SK하이닉스'] = int(price.text.replace(',', ''))
        
        # 삼성전자
        response = requests.get('https://finance.naver.com/item/main.naver?code=005930')
        soup = BeautifulSoup(response.content, 'html.parser')
        price = soup.find('span', {'class': 'blind'})
        if price:
            prices['삼성전자'] = int(price.text.replace(',', ''))
        
        print(f"✅ 현재가 수집 성공: {prices}")
        return True, prices
        
    except Exception as e:
        print(f"❌ 현재가 수집 실패: {e}")
        return False, {}

def calculate_portfolio(prices):
    """포트폴리오 계산"""
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
    
    return {
        'meritz_total': meritz_total,
        'future_total': future_total,
        'meritz_profit': meritz_profit,
        'future_profit': future_profit
    }

async def send_report(prices, calc):
    """일일 리포트 생성 및 발송"""
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
   • 수익률: +{(calc['meritz_profit']/ACCOUNT_INFO['메리츠']['원금']/10000)*100:.1f}%

🏦 미래에셋증권: {(calc['future_total'] + ACCOUNT_INFO['미래']['현금'])/10000:.0f}만원
   • 원금: 20,000만원
   • 수익금: +{calc['future_profit']/10000:.0f}만원
   • 수익률: +{(calc['future_profit']/ACCOUNT_INFO['미래']['원금']/10000)*100:.1f}%
   • 현금: 8,606만원"""
    
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report)
    print("✅ 리포트 발송 완료!")

def background_task():
    """백그라운드 작업"""
    try:
        success, prices = get_current_prices()
        if success:
            calc = calculate_portfolio(prices)
            asyncio.run(send_report(prices, calc))
    except Exception as e:
        print(f"오류: {e}")

if __name__ == "__main__":
    thread = threading.Thread(target=background_task, daemon=True)
    thread.start()
    
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
