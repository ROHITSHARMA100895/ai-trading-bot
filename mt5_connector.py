import MetaTrader5 as mt5
import config

def connect():
    if not mt5.initialize():
        raise Exception("MT5 init fail")
    if not mt5.login(config.MT5_LOGIN, config.MT5_PASSWORD, config.MT5_SERVER):
        raise Exception(f"Login fail: {mt5.last_error()}")
    print(f"✅ Connected. Balance: {mt5.account_info().balance}")

def send_order(symbol, order_type, lot, sl, tp):
    info = mt5.symbol_info(symbol)
    if info is None:
        print(f"❌ {symbol} not found")
        return None
    if not info.visible:
        mt5.symbol_select(symbol, True)
    tick = mt5.symbol_info_tick(symbol)
    if order_type == mt5.ORDER_TYPE_BUY:
        price = tick.ask
    else:
        price = tick.bid
    if info.spread > config.MAX_SPREAD_POINTS:
        print(f"📛 Spread too high for {symbol}: {info.spread}")
        return None
    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol,
        "volume": lot,
        "type": order_type,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 20,
        "magic": 123456,
        "comment": "AI_SAFE_BOT",
        "type_time": mt5.ORDER_TIME_GTC,
        "type_filling": mt5.ORDER_FILLING_IOC,
    }
    result = mt5.order_send(request)
    if result.retcode != mt5.TRADE_RETCODE_DONE:
        print(f"❌ Order failed: {result.comment}")
    else:
        print(f"✅ Trade placed: {symbol} {'BUY' if order_type==mt5.ORDER_TYPE_BUY else 'SELL'}, Lot={lot}, SL={sl}, TP={tp}")
    return result
