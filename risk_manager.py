import MetaTrader5 as mt5, pandas as pd, ta, config, numpy as np, datetime

def get_dynamic_risk():
    # Simplified Kelly based on last 20 trades
    history = mt5.history_deals_get(datetime.datetime.now()-datetime.timedelta(days=7), datetime.datetime.now())
    wins = sum(1 for d in history if d.profit > 0)
    total = len(history)
    if total > 10:
        win_rate = wins / total
        avg_win = np.mean([d.profit for d in history if d.profit > 0]) if wins else 0
        avg_loss = abs(np.mean([d.profit for d in history if d.profit < 0])) if (total-wins) else 1
        if avg_loss > 0:
            kelly = win_rate - ((1-win_rate) / (avg_win/avg_loss))
            risk = max(0.5, min(2.0, kelly * 100)) / 100
        else:
            risk = 1.0
    else:
        risk = 1.0
    return risk * config.RISK_PERCENT_PER_TRADE / 100

def calc_lot(symbol, balance, sl_price, entry_price):
    risk_fraction = get_dynamic_risk()
    info = mt5.symbol_info(symbol)
    if info is None: return 0.01
    sl_points = abs(entry_price - sl_price) / info.point
    if sl_points == 0: sl_points = 1
    pip_val = info.trade_tick_value * (10 if info.digits in (5,3) else 1)
    risk_cash = balance * risk_fraction
    lot = risk_cash / (sl_points * pip_val) if pip_val else 0.01
    lot = max(info.volume_min, min(info.volume_max, round(lot, 2)))
    return lot

def calc_sl_tp(symbol, order_type, entry):
    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H1, 0, 20)
    if rates is None: return entry*0.99, entry*1.01
    df = pd.DataFrame(rates)
    df['tr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
    atr = df['tr'].iloc[-1]
    sl_mult, tp_mult = 2.0, 3.0
    if order_type == mt5.ORDER_TYPE_BUY:
        sl = entry - atr * sl_mult
        tp = entry + atr * tp_mult
    else:
        sl = entry + atr * sl_mult
        tp = entry - atr * tp_mult
    digits = mt5.symbol_info(symbol).digits
    return round(sl, digits), round(tp, digits)

def daily_loss_check():
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    deals = mt5.history_deals_get(today, datetime.datetime.now())
    if deals is None: return False
    pnl = sum(d.profit for d in deals)
    bal = mt5.account_info().balance
    if bal == 0: return False
    loss_pct = -pnl / bal * 100
    return loss_pct >= config.DAILY_LOSS_LIMIT_PCT
