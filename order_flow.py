import MetaTrader5 as mt5

def get_order_flow(symbol):
    try:
        if mt5.symbol_info(symbol).trade_calc_mode == 0:  # forex
            book = mt5.market_book_get(symbol)
            if book:
                bid_vol = sum(b.volume for b in book if b.type == 0)
                ask_vol = sum(b.volume for b in book if b.type == 1)
                total = bid_vol + ask_vol
                if total > 0:
                    return (bid_vol - ask_vol) / total
    except: pass
    return 0
