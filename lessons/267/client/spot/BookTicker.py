import mexc_spot_v3
from decimal import Decimal


market = mexc_spot_v3.mexc_market()
trade = mexc_spot_v3.mexc_trade()

params = {
    "symbol": "SOLUSDT",
}

ticker = market.get_bookticker(params)

try:
    symbol = ticker['symbol']
    best_bid = Decimal(ticker['bidPrice'])
    best_bid_qty = Decimal(ticker['bidQty'])
    best_ask = Decimal(ticker['askPrice'])
    best_ask_qty = Decimal(ticker['askQty'])

    spread = best_ask - best_bid
    mid_price = (best_bid + best_ask) / 2

    place_bid_price = mid_price - (spread / 2) - Decimal(0.50)
    place_ask_price = mid_price + (spread / 2) + Decimal(0.50)

    # Handle use case if you match bid/ask and it was canceled by exhange (don't just let them know)
    # mention what is tick
    params = [{
        "symbol": 'SOLUSDT',
        "side": "BUY",
        "type": "LIMIT_MAKER",
        "quantity": 0.005,
        "price": str(place_bid_price)
    }, {
        "symbol": 'SOLUSDT',
        "side": "SELL",
        "type": "LIMIT_MAKER",
        "quantity": 0.005,
        "price": str(place_ask_price)
    }]
    orders = trade.post_batchorders(params)

except KeyError as e:
    print('Failed to get market data')

## Check every 1 minute
# 1. if boht orders in place, do nothing
# 2. if one order is filled check if price deviated by more then 2%, if yes cancel and cereate new orders, if no do nothing
# 3. you can increase the spread toward buy if you want to slowlly get inventory and make many while you doing so
