import json
import mexc_spot_v3
from decimal import Decimal

market = mexc_spot_v3.mexc_market()
trade = mexc_spot_v3.mexc_trade()

def handler(event, context):
    params = { "symbol": "SOLUSDT"}
    
    try:
        # Extract data from the event
        ticker = market.get_bookticker(params)

        best_bid = Decimal(ticker['bidPrice'])
        best_ask = Decimal(ticker['askPrice'])

        mid_price = (best_bid + best_ask) / 2

        trade.delete_openorders(params)

        spread = best_ask - best_bid
        place_bid_price = mid_price - (spread / 2) - Decimal(0.05)
        place_ask_price = mid_price + (spread / 2) + Decimal(0.05)

        params = [{
            "symbol": 'SOLUSDT',
            "side": "BUY",
            "type": "LIMIT_MAKER",
            "quantity": 0.01,
            "price": str(place_bid_price)
        }, {
            "symbol": 'SOLUSDT',
            "side": "SELL",
            "type": "LIMIT_MAKER",
            "quantity": 0.01,
            "price": str(place_ask_price)
        }]
        trade.post_batchorders(params)

        # Return successful response
        return { 
            'statusCode': 200, 
            'body': json.dumps({ 
                'new_mid_price': str(mid_price)}
        )}
    
    except Exception as e:
        return { 'statusCode': 500, 'body': json.dumps({ 'error': str(e) })}
