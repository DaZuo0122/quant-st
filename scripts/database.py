import os
import json
import datetime
import pandas as pd
import numpy as np


def create_folder():
    cur_dir = os.getcwd()
    new_path = cur_dir + "\\data"
    try:
        os.makedirs(new_path)
    except FileExistsError:
        pass
    # return cur_dir


class Dataset:
    def __init__(self, item_id: str, currency: str):
        self.item_id = item_id
        self.currency = currency
        self.data_set_high = pd.Series()
        self.data_set_low = pd.Series()

    def add_data(self, time, price, add_high: bool = True):
        # set add_high False to add data to data_set_low
        # time is used as index
        temp = pd.Series([price], index=[time])
        if add_high:
            self.data_set_high.append(temp)
        else:
            self.data_set_low.append(temp)
        del temp  # release memory

    def delete_data(self, time, delete_high: bool = True):
        # set delete_high False to delete data from data_set_low
        # pass time to delete corresponding data of price
        if delete_high:
            self.data_set_high.drop(time, inplace=True)  # modify without returning data
        else:
            self.data_set_low.drop(time, inplace=True)  # modify without returning data

    def read_json(self, item_id: str = self.item_id):
        # note: when called, self.currency will be changed to previously saved
        cur_path = os.getcwd()
        file_path = cur_path + '\\data\\' + item_id + '.json'
        with open(file_path, 'r') as file_loaded:
            csv_path_high = file_loaded['csv_path_high']
            csv_path_low = file_loaded['csv_path_low']
            self.currency = file_loaded['currency']
        df_h = pd.read_csv(csv_path_high)
        self.data_set_high = df_h.squeeze()

        df_l = pd.read_csv(csv_path_low)
        self.data_set_low = df_l.squeeze()

    def save_to_json(self, modify_currency=False):
        # it will create two file, a json to store item id and currency, a csv to store history data. file path of csv
        # will be also store in the json.
        cur_path = os.getcwd()
        if not os.path.exists(cur_path + '\\data'): create_folder()  # create a folder
        file_path_json = cur_path + '\\data\\' + self.item_id + '.json'
        file_path_csv_high = cur_path + '\\data\\' + self.item_id + '_high.csv'
        file_path_csv_low = cur_path + '\\data\\' + self.item_id + '_low.csv'
        data = {
            'item_id': self.item_id,
            'currency': self.currency,
            'csv_path_high': file_path_csv_high,
            'csv_path_low': file_path_csv_low
        }

        if os.path.exists(file_path_json):
            with open(file_path_json, 'r') as file_mod:
                data_mod = json.load(file_mod)
            # load and renew high data
            df_h = pd.read_csv(data_mod['csv_path_high'])
            data_to_load_h = df_h.squeeze()
            data_to_load_h.append(self.data_set_high)  # add new data to high
            data_to_load_h.to_csv(file_path_csv_high)  # save Series obj to csv file
            # load and renew low data
            df_l = pd.read_csv(data_mod['csv_path_low'])
            data_to_load_l = df_l.squeeze()
            data_to_load_l.append(self.data_set_low)  # add new data to high
            data_to_load_l.to_csv(file_path_csv_low)  # save Series obj to csv file

            if modify_currency:
                data_mod['currency'] = data['currency']
                with open(file_path_json, 'w') as update_file:
                    update_data = json.dumps(data_mod)
                    update_file.write(update_data)
                    update_file.close()

        else:
            with open(file_path_json, 'w') as file_json:
                json.dump(data, file_json)
                file_json.close()
            self.data_set_high.to_csv(file_path_csv_high)  # save data series high
            self.data_set_low.to_csv(file_path_csv_low)  # save data series low

'''
    def save_to_json(self, modify_currency=False):
        # set 'modify_currency' to Ture to change currency
        cur_path = os.getcwd()
        file_path = cur_path + '\\data\\' + self.item_id + '.json'
        data = {
                'item_id': self.item_id,
                'currency': self.currency,
                'history_price': self.data_set
            }
        if os.path.exists(file_path):
            with open(file_path, 'r') as file_mod:
                data_mod = json.load(file_mod)
            if modify_currency:
                data_mod['currency'] = data['currency']
            data_mod['history_price'] = data['history_price']
            with open(file_path, 'w') as update_file:
                update_data = json.dumps(data_mod)
                update_file.write(update_data)
                update_file.close()

        else:
            with open(file_path, 'w') as file_json:
                json.dump(data, file_json)
                file_json.close()
'''


