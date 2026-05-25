import MetaTrader5 as mt5, pandas as pd, ta, numpy as np, joblib, os

def get_technical_score(symbol):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 200)
    if rates is None or len(rates) < 50: return 0
    df = pd.DataFrame(rates)
    df['time'] = pd.to_datetime(df['time'], unit='s')
    # Indicators
    df['rsi'] = ta.momentum.RSIIndicator(df['close']).rsi()
    macd = ta.trend.MACD(df['close'])
    df['macd'] = macd.macd()
    df['macd_signal'] = macd.macd_signal()
    bb = ta.volatility.BollingerBands(df['close'])
    df['bb_lower'] = bb.bollinger_lband()
    df['bb_upper'] = bb.bollinger_hband()
    df['sma20'] = ta.trend.SMAIndicator(df['close'], 20).sma_indicator()
    df['sma50'] = ta.trend.SMAIndicator(df['close'], 50).sma_indicator()
    last = df.iloc[-1]
    score = 0
    if last['rsi'] < 30: score += 0.3
    elif last['rsi'] > 70: score -= 0.3
    if last['close'] < last['bb_lower']: score += 0.25
    elif last['close'] > last['bb_upper']: score -= 0.25
    if last['macd'] > last['macd_signal']: score += 0.2
    else: score -= 0.2
    if last['sma20'] > last['sma50']: score += 0.15
    else: score -= 0.15
    indicator_score = max(-1, min(1, score))
    # ML model
    ml_score = 0
    model_path = f"models/saved/xgb_{symbol.replace('=X','').replace('-','_')}.pkl"
    if os.path.exists(model_path):
        try:
            model = joblib.load(model_path)
            # Feature engineering
            df['return'] = df['close'].pct_change()
            df['sma10'] = df['close'].rolling(10).mean()
            df['volatility'] = df['return'].rolling(20).std()
            feats = ['return','sma10','sma50','volatility']
            X = df[feats].fillna(0).iloc[-1:].values
            prob = model.predict_proba(X)[0][1]
            ml_score = (prob - 0.5) * 2
        except: pass
    return max(-1, min(1, indicator_score*0.6 + ml_score*0.4))
