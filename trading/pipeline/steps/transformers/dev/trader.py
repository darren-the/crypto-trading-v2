from pipeline.base_classes.task import Task
import json

# TODO: temporary definitions for constants
LIMIT_BUY = 0
MARKET_BUY = 1
LIMIT_SELL = 2
MARKET_SELL = 3
MARKET_STOP_SELL = 4

MAKER_FEE = 0.001
TAKER_FEE = 0.002

class Trader(Task):
    def __init__(self, *args, **kwargs):
        self.risk = 0.05
        self.balance = 10000
        self.__dict__.update(kwargs)
        # TODO: currently positions, current_prices etc. are keyed on symbol but we only have 1 symbol so
        # this isn't an issue right now but in the future when more symbols are needed, a symbol combiner
        # parent class will need to be written with this class inheriting from it.
        self.position = {'base_price': -1, 'amount': 0}
        self.current_candle = {
            'timestamp': -1,
            'open': -1,
            'close': -1,
            'high': -1,
            'low': -1,
        }
        self.equity = self.balance
        self.orders = []
        self.transaction_history = []
        super().__init__()
        
    def process(self, element):
        # TODO: order history is for future implementation, slightly different to transaction history in that
        # not all orders will be executed since some may get cancelled
        # self.order_history = []
        self.transaction_history = []
        self.current_candle['open'] = element['open']
        self.current_candle['close'] = element['close']
        self.current_candle['high'] = element['high']
        self.current_candle['low'] = element['low']

        self._execute_orders()
        self._take_profit()

        if element['retracement_long']:
            amount = self._get_max_buyable_amount()
            risk_price = self.current_candle['close'] * (1 - self.risk)
            self._new_order(MARKET_BUY, self.current_candle['close'], amount)
            self._new_order(MARKET_STOP_SELL, risk_price, amount)

        return {
            'timestamp': element['timestamp'],
            'balance': self.balance,
            'equity': self.equity,
            'position_base_price': self.position['base_price'],
            'position_amount': self.position['amount'],
            'orders': json.dumps(self.orders),
            'transaction_history': json.dumps(self.transaction_history),
        }

    def _calculate_equity(self):
        self.equity = self.balance + self.current_candle['close'] * self.position['amount']
    
    def _get_max_buyable_amount(self):
        return self.balance / self.current_candle['close'] / (1 + TAKER_FEE)

    def _update_transactions(self, order):
        self.transaction_history.append({
            'timestamp': self.current_candle['timestamp'],
            'order_type': order['order_type'],
            'price': order['price'],
            'amount': order['amount'],
        })
    
    def _execute_orders(self):
        i = 0
        while i < len(self.orders):
            if self.current_candle['low'] <= self.orders[i]['price'] <= self.current_candle['high']:
                if self.orders[i]['order_type'] == MARKET_STOP_SELL:
                    self._market_sell(self.orders[i])
                # TODO: add conditions for LIMIT_BUY and LIMIT_SELL
                self.orders.pop(i)
            else:
                i += 1
                
    def _new_order(self, order_type, price, amount):
        order = {
            'order_type': order_type,
            'price': price,
            'amount': amount,
        }
        if order_type == MARKET_BUY:
            self._market_buy(order)
        elif order_type == MARKET_SELL:
            self._market_sell(order)
        elif order_type == MARKET_STOP_SELL:
            self._market_stop_sell(order)

    def _market_buy(self, order):
        if order['amount'] <= 0:
            return
        remaining_balance = self.balance - self.current_candle['close'] * order['amount'] * (1 + TAKER_FEE)
        if remaining_balance < 0:
            return -1
        self.balance = remaining_balance
        self.position['amount'] += order['amount']
        self.position['base_price'] = self.current_candle['close'] # TODO: calculate new base price
        self._update_transactions(order)
        self._calculate_equity()
    
    def _market_stop_sell(self, order):
        if order['price'] > self.current_candle['close'] or order['amount'] > self.position['amount']:
            return
        self.orders.append(order)
    
    def _market_sell(self, order):
        if order['amount'] <= 0:
            return
        self.balance += order['price'] * order['amount'] * (1 - TAKER_FEE)
        self.position['amount'] -= order['amount']
        if self.position['amount'] == 0:
            self.position['base_price'] = -1
        else:
            # TODO: calculate new base price
            pass
        self._update_transactions(order)
        self._calculate_equity()
    
    def _take_profit(self):
        if self.position['amount'] <= 0:
            return
        base_value = self.position['amount'] * self.position['base_price']
        new_value = self.position['amount'] * self.current_candle['close'] * (1 - TAKER_FEE)
        if (new_value - base_value) / base_value >= 0.01:
            self._new_order(MARKET_SELL, self.current_candle['close'], self.position['amount'])
        