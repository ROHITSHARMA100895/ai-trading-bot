import config, requests, yfinance as yf
from edgartools import Edgar

def get_fundamental_score(symbol):
    if symbol.endswith("USD") and symbol[:3] in ["BTC","ETH"]: return 0
    stock_list = ['AAPL','TSLA','MSFT','GOOGL','AMZN']
    if symbol.upper() not in stock_list: return 0
    score = 0
    # Finnhub metrics
    if config.FINNHUB_API_KEY:
        try:
            url = f"https://finnhub.io/api/v1/stock/metric?symbol={symbol}&metric=all&token={config.FINNHUB_API_KEY}"
            resp = requests.get(url, timeout=10)
            if resp.status_code==200:
                m = resp.json().get('metric',{})
                pe = m.get('peBasicExclExtraTTM')
                roe = m.get('roeTTM')
                de = m.get('totalDebt/totalEquityAnnual')
                growth = m.get('revenueGrowthTTMYoy')
                if pe:
                    if pe < 15: score += 0.3
                    elif pe > 40: score -= 0.2
                if roe and roe > 20: score += 0.2
                if de and de > 2: score -= 0.2
                if growth and growth > 0.1: score += 0.3
            # insider transactions
            url2 = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={config.FINNHUB_API_KEY}"
            resp2 = requests.get(url2, timeout=10)
            if resp2.status_code==200:
                txns = resp2.json().get('data',[])
                if txns:
                    buys = sum(1 for t in txns[:10] if t.get('change',0)>0)
                    sells = sum(1 for t in txns[:10] if t.get('change',0)<0)
                    if buys > sells: score += 0.15
                    elif sells > buys: score -= 0.15
        except: pass
    # yfinance fallback
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        pe = info.get('trailingPE')
        growth = info.get('revenueGrowth')
        de = info.get('debtToEquity')
        if pe:
            if pe < 15: score += 0.3
            elif pe > 40: score -= 0.2
        if growth and growth > 0.1: score += 0.3
        if de and de > 2: score -= 0.2
    except: pass
    # SEC EDGAR recent filing sentiment (simplified)
    try:
        edgar = Edgar()
        filings = edgar.get_filings(symbol, filing_type="10-K", count=1)
        if filings:
            # just a simple check: if they exist, mark neutral for now
            pass
    except: pass
    return max(-1, min(1, score))
