# -*- coding: utf-8 -*-
"""
Created on Wed Feb 13 23:21:50 2019

@author: yuanq
"""

from Enum import enum
from dateutil import parser

@enum.unique
class ENUM_SIDE(enum):
    LONG = 1
    SHORT = 2

@enum.unique
class ENUM_TRADE_STATUS(enum):
    ACTIVE = 1
    DEAD = 2

@enum.unique
class ENUM_INSTRUMENT(enum):
    CASH_EQUITY = 1
    EXCHANGE_TRADED_OPTION = 2
    VANILLA_OPTION = 3
    FUTURES = 4
    
class Data():
    def __init__(self, npa_last, 
                 npa_open = None, 
                 npa_high = None, 
                 npa_low = None, 
                 npa_volume = None):
        pass
    
    def __del__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass

class Portfolio():
    def __init__(self):
        self.__lst_positions = []
        
    def add_position(self, 
                     position):
        self.__lst_positions.append(position)
        return len(self.__lst_positions)-1
    
    def compute_pnl(self, 
                    bln_realised = True):
        if bln_realised:
            return sum([pos.get_pnl() for pos in self.__lst_positions if pos.get_trade_status() == ENUM_TRADE_STATUS.DEAD])
        else:
            return sum([pos.get_pnl() for pos in self.__lst_positions])

class Position():   
    def __init__(self, 
                 int_trade_id, 
                 str_trade_date, 
                 dbl_entry_price, 
                 dbl_entry_quantity, 
                 dbl_take_profit, 
                 dbl_stop_loss, 
                 enum_instrument = ENUM_INSTRUMENT.CASH_EQUITY, 
                 str_portfolio = None, 
                 **kwargs):
        self.__int_trade_id = int_trade_id
        self.__dte_trade_date = parser.parse(str_trade_date)
        self.__enum_status = ENUM_TRADE_STATUS.ACTIVE
        self.__dbl_entry_price = float(dbl_entry_price)
        self.__dbl_entry_quantity = float(dbl_entry_quantity)
        self.__dbl_take_profit = float(dbl_take_profit)
        self.__dbl_stop_loss = float(dbl_stop_loss)
        if self.__dbl_entry_quantity > 0:
            self.__enum_side = ENUM_SIDE.LONG
        else:
            self.__enum_side = ENUM_SIDE.SHORT
        self.__enum_instrument = ENUM_INSTRUMENT.CASH_EQUITY
        self.__str_portfolio = str_portfolio
        self.__dbl_pnl = 0.0
        
    def get_trade_id(self):
        return self.__int_trade_id
    
    def get_trade_date(self):
        return self.__dte_trade_date
    
    def get_trade_status(self):
        return self.__enum_status
    
    def get_entry_price(self):
        return self.__dbl_entry_price
    
    def get_entry_quantity(self):
        return self.__dbl_entry_quantity
    
    def get_take_profit(self):
        return self.__dbl_take_profit
    
    def get_stop_loss(self):
        return self.__dbl_stop_loss
    
    def get_instrument(self):
        return self.__enum_instrument
    
    def get_portfolio(self):
        return self.__str_portfolio
    
    def get_pnl(self):
        return self.__dbl_pnl
    
        