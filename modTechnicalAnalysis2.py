# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 00:03:52 2017

@author: Lim Yuan Qing
"""

import enum
from enum import Enum
import numpy as np
import pandas as pd

@enum.unique
class ENUM_MA_METHOD(Enum):
    SMA = 1
    EMA = 2
    SMMA = 3
    LWMA = 4

class TechnicalAnalysis():
    def __init__(self, df_data):
        self.df_data = df_data
        self.int_initial_col_count = df_data.shape[1]
            
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def __del__(self):
        pass
    
    def get_num_indicators(self):
        return self.df_data.shape[1] - self.int_initial_col_count
    
    def resample_data(self, strFreq):
        # http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        self.df_data = self.df_data.resample('W').last()
    
    def gen_rsi(self, 
                str_col_name, 
                int_period):
        
        df_dUp, df_dDown = (self.df_data[str_col_name].diff(), 
                            self.df_data[str_col_name].diff())
        df_dUp[df_dUp < 0] = 0
        df_dDown[df_dDown > 0] = 0

        self.df_data['RSI_' + str(str_col_name) + '_' + str(int_period) ] = (100 - 
                     (100/ (1 + df_dUp.rolling(window=int_period).mean() / 
                            df_dDown.rolling(window=int_period).mean().abs()))
                     )
        
        #yQ: do you want to break the long lines of codes? 
        
        #yQ: want smoothing? refer to rsi excel calculation file in dropbox
        
        #tested but dont tally because of smoothing process

    
    
    def gen_ma(self, 
               str_col_name, 
               int_period, 
               enum_method = ENUM_MA_METHOD.SMA):
        # model after iMA indicator in MQL4 (https://docs.mql4.com/indicators/ima)
        # supported methods are as per iMA (https://docs.mql4.com/constants/indicatorconstants/enum_ma_method)        
        str_name = enum_method.name + '_' + str(str_col_name) + '_'  + str(int_period)
        if enum_method is ENUM_MA_METHOD.SMA:
            self.df_data[str_name] = (
                    self.df_data[str_col_name].rolling(window=int_period).mean()
                    )
        elif enum_method is ENUM_MA_METHOD.EMA:
            self.df_data[str_name] = (
                    self.df_data[str_col_name].ewm(span=int_period,adjust=True).mean()
                    )
        elif enum_method is ENUM_MA_METHOD.SMMA:
            pass
        elif enum_method is ENUM_MA_METHOD.LWMA:
            self.df_data[str_name] = (
                    self.df_data[str_col_name].rolling(window=int_period).apply(self.linear_weighted_average, raw=True)
                    )
    
    def linear_weighted_average(self,np_array):
        length = np_array.shape[0]
        weights = np.linspace(1,length,length)
        return (np_array * weights).sum() / np.sum(weights)
    
    def gen_sma(self, str_col_name, int_period):
        
        self.df_data['SMA'] = self.df_data[str_col_name].rolling(window=int_period).mean()
        
        #yQ: split sma and ema in the event that we want to call only one of the ma-s. 
        #alternatively, to include the type of moving averages as parameter to function    
        
        #tested and passed
        
    def gen_ema(self, str_col_name, int_period):
        
        self.df_data['EMA_pandas'] = self.df_data[str_col_name].ewm(span=int_period,adjust=False).mean()
        
        #not tested
        

        
    def gen_bollinger_band (self, str_col_name, int_period, int_std_dev):
        
        self.df_data['BB_Upper'] = self.df_data[str_col_name].rolling(window=int_period).mean() + (self.df_data[str_col_name].rolling(window=int_period).std())*int_std_dev
        self.df_data['BB_Lower'] = self.df_data[str_col_name].rolling(window=int_period).mean() - (self.df_data[str_col_name].rolling(window=int_period).std())*int_std_dev 
        
        #tested and passed
        
    def gen_rate_of_change (self, str_col_name, int_period):
        
        self.df_data['ROC'] = self.df_data[str_col_name].diff(int_period)/self.df_data[str_col_name].shift(int_period)*100
                            
        #tested and passed
        
    def gen_commodity_channel_index (self, int_period, dbl_constant):
        
        #YQ: should dbl_constant be variable? 
        
        TP = (self.df_data['High'] + self.df_data['Low'] + self.df_data['Close'])/3
        #self.df_data['sma']= self.df_data['typical price'].rolling(window=int_period).mean()
        #self.df_data['mean deviation'] = self.df_data['typical price'].rolling(window=int_period).std()

        CCI = pd.Series((TP - TP.rolling(window=int_period, center = False).mean()) / (dbl_constant * TP.rolling(window=int_period, center=False).std()), name = 'CCI')
        self.df_data =  self.df_data.join(CCI) 
        
        #self.df_data['cci'] = (self.df_data['typical price'] - pd.rolling_mean(self.df_data['typical price'], int_period)) / (dbl_constant * pd.rolling_std(self.df_data['typical price'], int_period))  
        
        #(self.df_data['typical price'] -  self.df_data['sma']) / (dbl_constant * self.df_data['mean deviation'])
        
        #tested but failed
        
    def gen_ichimoku (self, str_col_name):
        
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        self.df_data['tenkan_sen'] = (self.df_data['High'].rolling(window=9).max() + self.df_data['Low'].rolling(window=9).min()) /2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        self.df_data['kijun_sen'] = (self.df_data['High'].rolling(window=26).max() + self.df_data['Low'].rolling(window=26).min()) / 2
        
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2)
        self.df_data['senkou_span_a'] = ((self.df_data['tenkan_sen'] + self.df_data['kijun_sen']) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        self.df_data['senkou_span_b'] = ((self.df_data['High'].rolling(window=52).max() + self.df_data['Low'].rolling(window=52).min()) / 2).shift(26)
        
        #Chikou Span (Lagging Span): Close plotted 26 days in the past
        self.df_data['chikou_span'] = self.df_data[str_col_name].shift(-22) # 22 according to investopedia
        
        #not tested
