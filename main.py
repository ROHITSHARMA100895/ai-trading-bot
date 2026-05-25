import time, schedule, MetaTrader5 as mt5, requests, config
from utils.mt5_connector import connect, send_order
from models.ensemble import should_trade
from risk_manager import calc_lot, calc_sl_tp, daily_loss_check
from self_updater import update_models, update_code

def trading_cycle():
    if daily_loss_check():
        print("⛔ Daily loss limit hit")
        return
    print("🔍 Scanning market...")
    acc = mt5.account_info()
    if acc is None:
        connect()
        return
    balance = acc.balance
    positions = mt5.positions_get()
    open_syms = [p.symbol for p in positions] if positions else []
    for sym in config.SYMBOLS:
        if sym in open_syms: continue
        if len(open_syms) >= config.MAX_OPEN_TRADES: break
        sig = should_trade(sym)
        if sig == "HOLD": continue
        tick = mt5.symbol_info_tick(sym)
        if tick is None: continue
        if sig == "BUY":
            otype = mt5.ORDER_TYPE_BUY
            entry = tick.ask
        else:
            otype = mt5.ORDER_TYPE_SELL
            entry = tick.bid
        sl, tp = calc_sl_tp(sym, otype, entry)
        lot = calc_lot(sym, balance, sl, entry)
        res = send_order(sym, otype, lot, sl, tp)
        if res:
            open_syms.append(sym)
            msg = f"🤖 {sym} {sig} Lot:{lot} SL:{sl} TP:{tp}"
            print(msg)
            if config.TELEGRAM_TOKEN:
                requests.post(f"https://api.telegram.org/bot{config.TELEGRAM_TOKEN}/sendMessage",
                              data={"chat_id": config.TELEGRAM_CHAT_ID, "text": msg})
        time.sleep(2)

if __name__ == "__main__":
    print("🌍 World's No.1 AI Trading Bot (Full Stack) Starting...")
    connect()
    trading_cycle()
    schedule.every(15).minutes.do(trading_cycle)
    schedule.every().sunday.at("03:00").do(lambda: (update_models(), update_code()))
    print("✅ Bot live. Aap sirf fund add karo, baaki automatic.")
    while True:
        schedule.run_pending()
        time.sleep(1)
