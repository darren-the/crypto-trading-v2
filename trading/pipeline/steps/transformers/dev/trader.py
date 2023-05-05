from pipeline.base_classes.task import Task
import json
from pipeline.configs.constants import MARKET_BUY, MARKET_SELL, MARKET_STOP_SELL, LIMIT_SELL

# TODO: temporary definitions for constants
MAKER_FEE = 0.001
TAKER_FEE = 0.002

BASELINE_SUP_FACTOR = 900_000

class Trader(Task):
    def __init__(self, *args, **kwargs):
        self.balance = 10000
        self.total_balance_risk = 0.01
        self.min_risk_reward_ratio = 1
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
        self.active_trade = False  # Temporary variable to track when a trade is active
        self.equity = self.balance
        self.orders = []
        self.transaction_history = []
        self.extra_output_names = ['transaction_history']
        super().__init__()
        
    def process(self, element):
        # TODO: order history is for future implementation, slightly different to transaction history in that
        # not all orders will be executed since some may get cancelled
        # self.order_history = []
        self.transaction_history = []
        self.current_candle['timestamp'] = element['timestamp']
        self.current_candle['open'] = element['open']
        self.current_candle['close'] = element['close']
        self.current_candle['high'] = element['high']
        self.current_candle['low'] = element['low']

        self._execute_orders()
        # self._take_profit()

        if element['retracement_long'] and not self.active_trade:
            risk_price, reward_price, risk_reward_ratio = self._get_risk_reward(element)
            if risk_reward_ratio > self.min_risk_reward_ratio:
                amount = self._get_buy_amount(risk_price) # * self._get_timeframe_scale(element)
                self._new_order(MARKET_BUY, self.current_candle['close'], amount)
                self._new_order(MARKET_STOP_SELL, risk_price, amount)
                self._new_order(LIMIT_SELL, reward_price, amount)
        
        # temp outputs
        recent_sup_top = -1
        recent_sup_bottom = -1
        risk = -1
        if element['retracement_long']:
            supports = json.loads(element['supports'])
            for support in supports:
                if support['sup_factor'] >= BASELINE_SUP_FACTOR:
                    recent_sup_top = support['sup_top']
                    recent_sup_bottom = support['sup_bottom']
                    risk = round((self.current_candle['close'] - recent_sup_bottom) / self.current_candle['close'], 4)
                    break
        
        self._calculate_equity()
        
        transaction_summary = []
        for transaction in self.transaction_history:
            transaction_summary.append(transaction['order_type'])

        return {
            'timestamp': element['timestamp'],
            'balance': self.balance,
            'equity': self.equity,
            'position_base_price': self.position['base_price'],
            'position_amount': self.position['amount'],
            'orders': json.dumps(self.orders),
            'transaction_history': self.transaction_history,
            'transaction_summary': json.dumps(transaction_summary),
            # temp outputs
            'recent_sup_top': recent_sup_top,
            'recent_sup_bottom': recent_sup_bottom,
            'risk': risk,
        }

    def _calculate_equity(self):
        self.equity = self.balance + self.current_candle['close'] * self.position['amount']
    
    def _get_buy_amount(self, risk_price):
        amount = self.total_balance_risk * self.balance / (self.current_candle['close'] - risk_price * (1 - TAKER_FEE))
        max_amount = self.balance / self.current_candle['close'] / (1 + TAKER_FEE)
        return min(amount, max_amount)
        
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
                if self.orders[i]['order_type'] == MARKET_STOP_SELL or self.orders[i]['order_type'] == LIMIT_SELL:
                    self._sell(self.orders.pop(i))
                # TODO: add conditions for LIMIT_BUY
            else:
                i += 1
                
    def _new_order(self, order_type, price, amount):
        order = {
            'order_type': order_type,
            'price': price,
            'amount': amount,
        }
        if order['amount'] <= 0:
            return
        if order_type == MARKET_BUY:
            self._buy(order)
        elif order_type == MARKET_SELL:
            self._sell(order)
        elif order_type == MARKET_STOP_SELL or order_type == LIMIT_SELL:
            self._create_sell_order(order)
        
    def _cancel_orders(self, order_type=None):
        if order_type is None:
            self.orders = []
        else:
            i = 0
            while i < len(self.orders):
                if order_type == self.orders[i]['order_type']:
                    self.orders.pop(i)
                else:
                    i += 1

    def _buy(self, order):
        if order['order_type'] == MARKET_SELL or order['order_type'] == MARKET_STOP_SELL:
            fee = TAKER_FEE
        else:
            fee = MAKER_FEE
        remaining_balance = self.balance - self.current_candle['close'] * order['amount'] * (1 + fee)
        if remaining_balance < 0:
            return -1
        self.balance = remaining_balance
        self.position['amount'] += order['amount']
        self.position['base_price'] = self.current_candle['close'] # TODO: calculate new base price
        self.active_trade = True
        self._update_transactions(order)
    
    def _create_sell_order(self, order):
        if order['amount'] > self.position['amount']:
            return
        if order['order_type'] == MARKET_STOP_SELL and order['price'] > self.current_candle['close']:
            return
        if order['order_type'] == LIMIT_SELL and order['price'] < self.current_candle['close']:
            return
        self.orders.append(order)
    
    def _sell(self, order):
        if order['order_type'] == MARKET_SELL or order['order_type'] == MARKET_STOP_SELL:
            fee = TAKER_FEE
            self._cancel_orders(LIMIT_SELL)
        else:
            fee = MAKER_FEE
            self._cancel_orders(MARKET_STOP_SELL)
        self.balance += order['price'] * order['amount'] * (1 - fee)
        self.position['amount'] -= order['amount']
        if self.position['amount'] == 0:
            self.position['base_price'] = -1
        else:
            # TODO: calculate new base price
            pass
        self._update_transactions(order)
        self.active_trade = False
    
    # def _take_profit(self):
    #     if self.position['amount'] <= 0:
    #         return
    #     base_value = self.position['amount'] * self.position['base_price']
    #     new_value = self.position['amount'] * self.current_candle['close'] * (1 - TAKER_FEE)
    #     if (new_value - base_value) / base_value >= 0.01:
    #         self._cancel_orders(MARKET_STOP_SELL)
    #         self._new_order(MARKET_SELL, self.current_candle['close'], self.position['amount'])
            
    def _get_risk_reward(self, element):
        supports = json.loads(element['supports'])
        for support in supports:
            if support['sup_factor'] >= BASELINE_SUP_FACTOR:
                risk_price = support['sup_bottom'] - element['risk_delta']
                reward_price = element['reward_price']
                reward = reward_price * (1 - MAKER_FEE) - element['close']
                risk = element['close'] - risk_price * (1 - TAKER_FEE)
                return risk_price, reward_price, reward / risk  # reward / risk is easier to calculate than the other way around
        return -1, -1, -1
    
    # def _get_timeframe_scale(self, element):
    #     scale = {
    #         '1m': 0,
    #         '5m': 0.15,
    #         '15m': 0.35,
    #         '1h': 0.65,
    #         '4h': 0.85,
    #         '1D': 1,
    #     }
    #     return scale[element['retracement_timeframe']]