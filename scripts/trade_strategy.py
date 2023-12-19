import pandas as pd
import numpy as np
from steampy.client import SteamClient
from steampy.models import GameOptions, Currency
from database import Dataset
import time


# Note: pass instance of steam client as para, to use methods below.
class Market_monitor():
    def __init__(self, client: SteamClient, item_name: str, game_name= GameOptions.CS, currency= 'US'):
        # default game is cs
        self.steam_client = client
        self.item_name = item_name
        self.game_name = game_name
        self.data_set = Dataset(item_name, currency)

    def get_cur_price(self, res_currency=Currency.USD) -> list | bool:
        # note: May rise TooManyRequests exception if used more than 20 times in 60 seconds
        # default currency is USD
        # it will a float number or False(get price unsuccessfully
        price = self.steam_client.market.fetch_price(self.item_name, game=self.game_name, currency=res_currency)
        # price == {'volume': '208', 'lowest_price': '$11.30 USD', 'median_price': '$11.33 USD', 'success': True}
        if price['success']:
            cur_price = [float(price['lowest_price'][1:6]), float(price['median_price'][1:6])]
            # cur_price = float(cur_price)
            return cur_price
        else:
            return False

    def get_history_price(self) -> list:
        pass
        res = self.steam_client.market.fetch_price_history(self.item_name, self.game_name)
        return res['prices']


class Dual_Thrust():
    # Note: trade logic is not perfect, use simple trade to reduce risk!!!
    def __init__(self, client: SteamClient, item: str, game: GameOptions = GameOptions.CS, n: int = 4, k1: float = 0.5, k2: float = 0.5):
        self.n = n
        self._k1 = k1
        self._k2 = k2
        self.steam_client = client
        self.item_id = item
        self.game = game
        self.monitor = Market_monitor(client, item, game_name=game)

    def dual_thrust_strategy(self, data: Dataset, item_hash_id: str):
        # calculate highest lowest and close price in n days
        high = data.data_set_high.rolling(window=self.n).max()
        low = data.data_set_low.rolling(window=self.n).min()
        close_price = self.monitor.get_history_price()
        close = pd.DataFrame(close_price[-2])

        # calculate range
        range_value = np.maximum(high - low, high.shift(1) - close.shift(1))

        price = self.monitor.get_cur_price()
        if price:
            # calculate upper and lower bound
            upper_bound = float(price[1]) + self._k1 * range_value
            lower_bound = float(price[1]) - self._k2 * range_value

        # generate signal
            signal = np.where(close > upper_bound, 1, np.where(close < lower_bound, -1, 0))

            return signal

    def trade(self, signal):
        fee_rate = float(0.15)
        price = self.monitor.get_cur_price()
        if signal:
            sell_p = str(int((float(price[0])*(1-fee_rate))*100))
            self.steam_client.create_sell_order(self.item_id, self.game, sell_p)
        else:
            buy_p = str(int(price[0]*100))
            self.steam_client.create_buy_order(self.item_id, self.game, buy_p)



class Simple_trade():
    def __init__(self, client: SteamClient, item_name: str, game=GameOptions.CS, currency=Currency.USD, fee_rate: float = 0.15):
        self.item_name = item_name
        self.currency = currency
        self.game = game
        self.fee_rate = fee_rate
        self.steam_client = client
        self.m = Market_monitor(self.steam_client, self.item_name, game_name=self.game)

    def market_sell(self, target_price: float, quantity: int, item_id: str) -> bool:
        price = self.m.get_cur_price(res_currency=self.currency)
        if price:
            mid_price = price[1]
            while quantity:
                if target_price*self.fee_rate <= mid_price:
                    sell_price = str(int(target_price*100))
                    # market_sell()
                    self.steam_client.create_sell_order(item_id, self.game, sell_price)
                quantity -= 1
            return True
        else:
            return False

    def market_buy(self, upper_bound: float, quantity: int, waiting_time: int = 19) -> bool:
        price = self.m.get_cur_price(res_currency=self.currency)
        if price:
            lowest_price = price[0]
            while waiting_time:
                if upper_bound >= lowest_price:
                    buy_price = str(int(lowest_price*100))
                    self.steam_client.create_buy_order(self.item_name, buy_price, quantity, self.game, currency=self.currency)
                    return True
                time.sleep(1)
                waiting_time -= 1
        else:
            return False

