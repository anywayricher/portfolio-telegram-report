import os
import asyncio
import threading
from datetime import datetime
from flask import Flask
from telegram import Bot
import yfinance as yf

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# 고정 포트폴리오 데이터
PORTFOLIO = {
    'SK하이닉스': {'수량': 50, '평단가': 2870340, '계좌': '메리츠', 'symbol': '000660.KS'},
    '삼성전자': {'수량': 347, '평단가': 351751, '계좌': '메리츠', 'symbol': '005930.KS'},
    '서진시스템': {'수량': 1, '평단가': 57800, '계좌': '메리츠', 'symbol': '013570.KS'},
    'KODEX S&P500': {'수량': 2354, '평단가': 25485, '계좌': '미래', 'symbol': '069500.KS'},
    'KODEX 나스닥100': {'수량': 2062, '평단가': 29090, '계좌': '미래', 'symbol': '066840.KS'},
    'KODEX AI반도체TOP': {'수량': 2465, '평단가': 52163, '계좌': '미래', 'symbol': '395160.KS'},
}

ACCOUNT_INFO = {
    '메리츠': {'원금': 14100, '현금': 0},
    '미래': {'원금': 20000, '현금': 8606}
}

# 메시지 발송 여부 (중복 방지)
message_sent_today = False

@app.route('/')
def hello():
    return "Portfolio Reporter is running!", 200

def get_current_prices():
    """yfinance에서 실시간 현재가 수집"""
    print("[DEBUG] 현재가 수집 시작...")
    
    try:
        prices = {}
        
        for ticker, data in PORTFOLIO.items():
            symbol = data['symbol']
            print(f"[DEBUG] {ticker} ({symbol}) 수집 중...")
            
            try:
                stock = yf.Ticker(symbol)
                current_price = stock.info.get('currentPrice') or stock.info.get('regularMarketPrice')
                
                if current_price:
                    prices[ticker] = int(current_price)
                    print(f"[DEBUG] {ticker}: {current_price}원")
                else:
                    print(f"[DEBUG] {ticker}: 가격 없음, 최근가 사용")
                    hist = stock.history(period='1d')
                    if not hist.empty:
                        prices[ticker] = int(hist['Close'].iloc[-1])
            except Exception as e:
                print(f"[DEBUG] {ticker} 수집 실패: {e}")
        
        print(f"[DEBUG] ✅ 현재가 수집 완료: {len(prices)}개")
        return True, prices
        
    except Exception as e:
        print(f"[DEBUG] ❌ 현재가 수집 실패: {e}")
        import traceback
        traceback.print_exc()
        return False, {}

def calculate_portfolio(prices):
    """포트폴리오 계산"""
    print("[DEBUG] 포트폴리오 계산 시작...")
    
    meritz_data = {'total': 0, 'profit': 0, 'holdings': []}
    future_data = {'total': 0, 'profit': 0, 'holdings': []}
    
    for ticker, data in PORTFOLIO.items():
        if ticker in prices:
            current_price = prices[ticker]
            quantity = data['수량']
            avg_price = data['평단가']
            account = data['계좌']
            
            eval_amount = current_price * quantity
            profit = eval_amount - (avg_price * quantity)
            profit_rate = (profit / (avg_price * quantity)) * 100 if (avg_price * quantity) != 0 else 0
            
            holding_info = {
                'ticker': ticker,
                'quantity': quantity,
                'avg_price': avg_price,
                'current_price': current_price,
                'eval_amount': eval_amount,
                'profit': profit,
                'profit_rate': profit_rate
            }
            
            if account == '메리츠':
                meritz_data['total'] += eval_amount
                meritz_data['profit'] += profit
                meritz_data['holdings'].append(holding_info)
            else:
                future_data['total'] += eval_amount
                future_data['profit'] += profit
                future_data['holdings'].append(holding_info)
    
    print(f"[DEBUG] ✅ 계산 완료")
    
    return meritz_data, future_data

async def send_report(prices, meritz_data, future_data):
    """일일 리포트 생성 및 발송"""
    global message_sent_today
    
    print("[DEBUG] 리포트 생성 시작...")
    
    # 이미 오늘 발송했으면 스킵
    if message_sent_today:
        print("[DEBUG] 오늘 이미 발송됨 - 중복 방지")
        return
    
    bot = Bot(token=TELEGRAM_TOKEN)
    
    total_asset = meritz_data['total'] + future_data['total'] + 86060000
    total_profit = meritz_data['profit'] + future_data['profit']
    total_original = 141000000 + 200000000
    total_return = (total_profit / total_original) * 100
    
    meritz_return = (meritz_data['profit'] / 141000000) * 100
    future_return = (future_data['profit'] / 200000000) * 100
    
    report = f"""📊 포트폴리오 일일 리포트
📅 {datetime.now().strftime('%Y-%m-%d')}

💰 현재 자산: {total_asset/10000:.0f}만원
💵 현재 수익금: +{total_profit/10000:.0f}만원
📊 현재 수익률: +{total_return:.1f}%

🏦 메리츠증권: {meritz_data['total']/10000:.0f}만원
   • 원금: 14,100만원
   • 수익금: +{meritz_data['profit']/10000:.0f}만원
   • 수익률: +{meritz_return:.1f}%"""
    
    for holding in meritz_data['holdings']:
        report += f"""

   📍 {holding['ticker']} ({holding['quantity']}주)
   평단가: {holding['avg_price']:,}원 → 현재가: {holding['current_price']:,}원
   평가액: {holding['eval_amount']/10000:.0f}만원 | 손익: {holding['profit']/10000:.0f}만원 ({holding['profit_rate']:.2f}%)"""
    
    report += f"""

🏦 미래에셋증권: {(future_data['total'] + 86060000)/10000:.0f}만원
   • 원금: 20,000만원
   • 수익금: +{future_data['profit']/10000:.0f}만원
   • 수익률: +{future_return:.1f}%
   • 현금: 8,606만원"""
    
    for holding in future_data['holdings']:
        report += f"""

   📍 {holding['ticker']} ({holding['quantity']}주)
   평가손익: {holding['profit']/10000:.0f}만원 ({holding['profit_rate']:.2f}%)"""
    
    print(f"[DEBUG] Telegram 발송 시작...")
    await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=report)
    print("✅ 리포트 발송 완료!")
    
    message_sent_today = True

def background_task():
    """백그라운드 작업"""
    print("[DEBUG] 백그라운드 작업 시작!")
    
    try:
        success, prices = get_current_prices()
        if success and prices:
            meritz_data, future_data = calculate_portfolio(prices)
            asyncio.run(send_report(prices, meritz_data, future_data))
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
    print("[DEBUG] 백그라운드 스레드 생성됨")
    
    port = int(os.getenv('PORT', 5000))
    print(f"[DEBUG] Flask 서버 시작 - 포트: {port}")
    app.run(host='0.0.0.0', port=port, threaded=True)
