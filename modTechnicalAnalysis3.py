# -*- coding: utf-8 -*-
"""
Created on Sun Mar 26 00:03:52 2017

@author: Lim Yuan Qing
"""

import enum
from enum import Enum
import numpy as np
import pandas as pd
import modPandasUtils3 as pdu
from sklearn.preprocessing import OneHotEncoder

@enum.unique
class ENUM_MA_METHOD(Enum):
    SMA = 1
    EMA = 2
    SMMA = 3
    LWMA = 4
    
@enum.unique
class ENUM_BINARY_METHOD(Enum):
    EXCEED = 1
    WITHIN = 2

class TechnicalAnalysis():
    def __init__(self, df_data):
        self.__df_data = df_data
        self.__int_initial_col_count = df_data.shape[1]
        self.__lst_indicator_names = []
            
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def __del__(self):
        pass
    
    def get_num_indicators(self):
        """
        Gets total number of indicators that were previously generated.
              
        Returns
        -------
        int
            total number of indicators that were previously generated.
            
        """
        return self.__df_data.shape[1] - self.__int_initial_col_count
    
    def get_indicator_names(self):
        """
        Gets column names of all indicators that were previously generated.
              
        Returns
        -------
        list
            contains column names of all indicators that were previously 
            generated.
            
        """
        return self.__lst_indicator_names
    
    def get_data(self, bln_drop_na=True, bln_indicators_only = False):
        """
        Returns pandas DataFrame `__df_data` data member of `TechnicalAnalysis` 
        class.
        
        Parameters
        ----------
        bln_drop_na : boolean, optional
            drop rows with empty cells in any of the columns (the default is 
            True - all rows with any empty cells are dropped from `__df_data`)
        
        Returns
        -------
        pandas DataFrame
            complete dataset with all technical indicators that were previously
            generated.
            
        """
        if bln_drop_na:
            if bln_indicators_only:
                return self.__df_data.dropna(how='any',inplace=False)[self.get_indicator_names()]
            else:
                return self.__df_data.dropna(how='any',inplace=False)
        else:
            if bln_indicators_only:
                return self.__df_data[self.get_indicator_names()]
            else:
                return self.__df_data
        
    def resample_data(self, strFreq):
        # http://pandas.pydata.org/pandas-docs/stable/timeseries.html#offset-aliases
        self.__df_data = self.__df_data.resample('W').last()
    
    def gen_one_hot_encoding(self, str_col_name):
        """
        Generates one hot encoding for `str_col_name`. All categories are
        appended to pandas DataFrame, `__df_data`, data member of the TechnicalAnalysis
        class.
        
        Parameters
        ----------
        str_col_name : string
            column name of categorical variable to be encoded
        
        Returns
        -------
        boolean
            True if indicator generated without an error.
            
        """
        try:
            df_one_hot = pd.get_dummies(
                                        self.__df_data[str_col_name], 
                                        prefix=str_col_name)
            self.__df_data = pd.concat([self.__df_data, df_one_hot], axis=1, sort=False)
            for col_name in df_one_hot.columns:
                self.__lst_indicator_names.append(col_name)
            return True
        except:
            return False
        
    
    def gen_crossover(self, str_col_name1, str_col_name2, bln_1_over_2 = True):
        """
        Generates binary variable to indicate if `col_name1` crosses `col_name2`.
        
        Parameters
        ----------
        str_col_name1 : string
            column name of variable to be used in computation of the RSI indicator
        str_col_name2 : string
            number of periods for use in the computation of the RSI indicator        
        bln_1_over_2 : boolean, optional 
            True to indicate periods where `str_col_name1` crosses over `str_col_name2`
            (the default is True where 1.0 indicates that `str_col_name1` crossed
            over `str_col_name2`)
        
        Returns
        -------
        boolean
            True if indicator generated without an error.
            
        """
        prev_1 = self.__df_data[str_col_name1].shift(1)
        prev_2 = self.__df_data[str_col_name2].shift(1)
        #try:
        if bln_1_over_2:
            str_indicator_name = str_col_name1 + '_crossover_' + str_col_name2
            self.__df_data[str_indicator_name] = np.where((prev_1<prev_2)&
                          (self.__df_data[str_col_name1]>=self.__df_data[str_col_name2]),
                          1.0,0.0)
        else:
            str_indicator_name = str_col_name2 + '_crossover_' + str_col_name1
            self.__df_data[str_indicator_name] = np.where((prev_1>prev_2)&
                          (self.__df_data[str_col_name1]<=self.__df_data[str_col_name2]),
                          1.0,0.0)
        self.__df_data[str_indicator_name] = pdu.optimize_mem_usage(
                                                self.__df_data[str_indicator_name])
        self.__lst_indicator_names.append(str_indicator_name)            
        return True
        #except:
        #    return False
    
        #https://stackoverflow.com/questions/28345261/python-and-pandas-moving-average-crossover
    
    def gen_rsi(self, 
                str_col_name, 
                int_period):
        """
        Generates the Relative Strength Index (RSI) technical indicator and appends
        it to the pandas DataFrame, `df_data`, data member of the `TechnicalAnalysis`
        class. Technically, function can be called on any variable of numeric type.
        
        Parameters
        ----------
        str_col_name : string
            column name of variable to be used in computation of the RSI indicator
        int_period : integer
            number of periods for use in the computation of the RSI indicator        
        
        Returns
        -------
        boolean
            True if indicator generated without an error.
            
        """
        try:
            df_dUp, df_dDown = (self.__df_data[str_col_name].diff(), 
                                self.__df_data[str_col_name].diff())
            df_dUp[df_dUp < 0] = 0
            df_dDown[df_dDown > 0] = 0
    
            str_indicator_name = 'RSI_' + str(str_col_name) + '_' + str(int_period) 
    
            self.__df_data[str_indicator_name] = pdu.optimize_mem_usage(100 - 
                         (100/ (1 + df_dUp.rolling(window=int_period).mean() / 
                                df_dDown.rolling(window=int_period).mean().abs()))
                         )
            self.__lst_indicator_names.append(str_indicator_name)
            return True
        except:
            return False
        
        #yQ: do you want to break the long lines of codes? 
        
        #yQ: want smoothing? refer to rsi excel calculation file in dropbox
        
        #tested but dont tally because of smoothing process

    def gen_ma(self, 
               str_col_name, 
               int_period, 
               enum_method = ENUM_MA_METHOD.SMA):
        """
        Generates the Moving Average technical indicator and appends it to the 
        pandas DataFrame, `df_data`, data member of the `TechnicalAnalysis`. 
        Technically, function can be called on any variable of numeric type.
        
        Parameters
        ----------
        str_col_name : string
            column name of variable to be used in computation of the Moving
             Average indicator
        int_period : integer
            number of periods for use in the computation of the RSI indicator        
        enum_method : ENUM_MA_METHOD
            enum to determine the type of moving average to compute: SMA, EMA, SMMA, LWMA
        
        Returns
        -------
        boolean
            True if indicator generated without an error.
            
        """
        # model after iMA indicator in MQL4 (https://docs.mql4.com/indicators/ima)
        # supported methods are as per iMA (https://docs.mql4.com/constants/indicatorconstants/enum_ma_method)        
        str_indicator_name = (enum_method.name + '_' + str(str_col_name) + '_'  
                              + str(int_period))
        try:
            if enum_method is ENUM_MA_METHOD.SMA:
                self.__df_data[str_indicator_name] = self.__df_data[str_col_name].rolling(window=int_period).mean()
                        
            elif enum_method is ENUM_MA_METHOD.EMA:
                self.__df_data[str_indicator_name] = self.__df_data[str_col_name].ewm(span=int_period,adjust=True).mean()
                        
            elif enum_method is ENUM_MA_METHOD.SMMA:
                pass
            elif enum_method is ENUM_MA_METHOD.LWMA:
                self.__df_data[str_indicator_name] = self.__df_data[str_col_name].rolling(window=int_period).apply(self.linear_weighted_average, raw=True)
                        
            self.__df_data[str_indicator_name] = pdu.optimize_mem_usage(
                                                    self.__df_data[str_indicator_name])
            self.__lst_indicator_names.append(str_indicator_name)
            return True
        except:
            return False
    
    def linear_weighted_average(self,np_array):
        length = np_array.shape[0]
        weights = np.linspace(1,length,length)
        return (np_array * weights).sum() / np.sum(weights) 
    
    def gen_rate_of_change(self, str_return_def):
        """
        Generates rate of change of given column and appends it to the 
        pandas DataFrame, `df_data`, data member of the `TechnicalAnalysis`. 
        Technically, function can be called on any variable of numeric type.
        
        Parameters
        ----------
        str_return_def : string
            return definition in the form of numerator|offset(operator)denominator|offset
        
        Returns
        -------
        boolean
            True if indicator generated without an error.            
        """
        try:
            lst_return_def = str_return_def.split('/')
            
            lst_num = lst_return_def[0].split('|')
            str_num_return_def = lst_num[0]
            int_num_period = int(lst_num[1])
            
            lst_denom = lst_return_def[1].split('|')
            str_denom_return_def = lst_denom[0]
            int_denom_period = int(lst_denom[1])
            
            self.__df_data[str_return_def] = pdu.optimize_mem_usage(
                np.log(self.__df_data[str_num_return_def].shift(int_num_period) / 
                self.__df_data[str_denom_return_def].shift(int_denom_period))
                )
            self.__lst_indicator_names.append(str_return_def)
            return True
        except:
            return False
    
    def gen_binary(self, 
                   str_col_name, 
                   dbl_lower_bound=None, 
                   dbl_upper_bound=None, 
                   enum_method=ENUM_BINARY_METHOD.EXCEED):
        """
        Generates binary variable based on specified condition.
        
        Parameters
        ----------
        str_col_name : string
            column name of variable to be used in computation of the binary 
            variable
        dbl_lower_bound : double
            lower bound of condition
        dbl_upper_bound : double
            upper_bound of condition
        enum_method : ENUM_BINARY_METHOD
            enum to determine the conditon type: EXCEED, WITHIN
        
        Returns
        -------
        boolean
            True if indicator generated without an error.            
        """
        try:
            if dbl_lower_bound == None and dbl_upper_bound == None:
                raise ValueError('`dbl_lower_bound` and `dbl_upper_bound` cannot both be `None`.')
            else:
                str_indicator_name = str_col_name + '_' + enum_method.name + '_' + str(dbl_lower_bound) + '|' +  str(dbl_upper_bound)
                if enum_method == ENUM_BINARY_METHOD.EXCEED:
                    if dbl_lower_bound == None:
                        self.df_data[str_indicator_name] = np.where(self.df_data[str_col_name] >= dbl_upper_bound,1.0, 0.0)
                    elif dbl_upper_bound == None:
                        self.df_data[str_indicator_name] = np.where(self.df_data[str_col_name] <= dbl_lower_bound, 1.0, 0.0)
                    else:
                        self.df_data[str_indicator_name] = np.where((self.df_data[str_col_name] >= dbl_upper_bound)
                                                            | (self.df_data[str_col_name] <= dbl_lower_bound), 1.0, 0.0)
                elif enum_method == ENUM_BINARY_METHOD.WITHIN:
                    if dbl_lower_bound == None:
                        self.df_data[str_indicator_name] = np.where(self.df_data[str_col_name] <= dbl_upper_bound,1.0,0.0)
                    elif dbl_upper_bound == None:
                        self.df_data[str_indicator_name] = np.where(self.df_data[str_col_name] >= dbl_lower_bound,1.0,0.0)
                    else:
                        self.df_data[str_indicator_name] = np.where((self.df_data[str_col_name] <= dbl_upper_bound)
                                                            & (self.df_data[str_col_name] >= dbl_lower_bound),1.0,0.0)
                else:
                    raise ValueError('''Invalid `enum_method` ENUM. Please see ENUM_BINARY_METHOD 
                                     for supported enumerations.''')
                self.df_data[str_indicator_name] = pdu.optimize_mem_usage(
                                                        self.df_data[str_indicator_name]
                                                    )
                self.__lst_indicator_names.append(str_indicator_name)
                return True
        except:
            return False
    
    def gen_standard_deviation(self, str_col_name, int_period):
        """
        Generates standard deviation of given column and appends it to the 
        pandas DataFrame, `df_data`, data member of the `TechnicalAnalysis`. 
        Technically, function can be called on any variable of numeric type.
        
        Parameters
        ----------
        str_col_name : string
            column name of variable to be used in computation of its standard 
            deviation
        int_period : integer
            number of periods for use in the computation of its standard deviation
                
        Returns
        -------
        boolean
            True if indicator generated without an error.            
        """
        str_indicator_name = 'STD_' + str(str_col_name) + '_' + str(int_period)
        try:
            self.__df_data[str_indicator_name] = pdu.optimize_mem_usage(
                                               self.__df_data[str_col_name].rolling(window=int_period).std()
                                               )
            self.__lst_indicator_names.append(str_indicator_name)
            return True
        except:
            return False    
    
    def gen_bollinger_band (self, str_col_name, int_period, int_std_dev):
        
        self.__df_data['BB_Upper'] = self.__df_data[str_col_name].rolling(window=int_period).mean() + (self.__df_data[str_col_name].rolling(window=int_period).std())*int_std_dev
        self.__df_data['BB_Lower'] = self.__df_data[str_col_name].rolling(window=int_period).mean() - (self.__df_data[str_col_name].rolling(window=int_period).std())*int_std_dev 
        
        #tested and passed
        
    
        
    def gen_commodity_channel_index (self, int_period, dbl_constant):
        
        #YQ: should dbl_constant be variable? 
        
        TP = (self.__df_data['High'] + self.__df_data['Low'] + self.__df_data['Close'])/3
        #self.__df_data['sma']= self.__df_data['typical price'].rolling(window=int_period).mean()
        #self.__df_data['mean deviation'] = self.__df_data['typical price'].rolling(window=int_period).std()

        CCI = pd.Series((TP - TP.rolling(window=int_period, center = False).mean()) / (dbl_constant * TP.rolling(window=int_period, center=False).std()), name = 'CCI')
        self.__df_data =  self.__df_data.join(CCI) 
        
        #self.__df_data['cci'] = (self.__df_data['typical price'] - pd.rolling_mean(self.__df_data['typical price'], int_period)) / (dbl_constant * pd.rolling_std(self.__df_data['typical price'], int_period))  
        
        #(self.__df_data['typical price'] -  self.__df_data['sma']) / (dbl_constant * self.__df_data['mean deviation'])
        
        #tested but failed
        
    def gen_ichimoku (self, str_col_name):
        
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2))
        self.__df_data['tenkan_sen'] = (self.__df_data['High'].rolling(window=9).max() + self.__df_data['Low'].rolling(window=9).min()) /2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2))
        self.__df_data['kijun_sen'] = (self.__df_data['High'].rolling(window=26).max() + self.__df_data['Low'].rolling(window=26).min()) / 2
        
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2)
        self.__df_data['senkou_span_a'] = ((self.__df_data['tenkan_sen'] + self.__df_data['kijun_sen']) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2))
        self.__df_data['senkou_span_b'] = ((self.__df_data['High'].rolling(window=52).max() + self.__df_data['Low'].rolling(window=52).min()) / 2).shift(26)
        
        #Chikou Span (Lagging Span): Close plotted 26 days in the past
        self.__df_data['chikou_span'] = self.__df_data[str_col_name].shift(-22) # 22 according to investopedia
        
        #not tested

    def gen_fibonacci_retracement(self, str_col_name, int_period):
        """
        Generates fibonacci retracement of given column and appends it to the 
        pandas DataFrame, `df_data`, data member of the `TechnicalAnalysis`. 
        Technically, function can be called on any variable of numeric type.
        
        Parameters
        ----------
        str_col_name : string
            column name of variable to be used in computation of its fibonacci 
            retracement
        int_period : integer
            number of periods for use in the computation of its fibonacci retracement
                
        Returns
        -------
        boolean
            True if indicator generated without an error.            
        """
        try:
            lst_ratios = [0.618, 0.382, 0.236]
                    
            max_price = self.__df_data[str_col_name].rolling(window=int_period).max()
            min_price = self.__df_data[str_col_name].rolling(window=int_period).min()
            diff = max_price - min_price
                    
            str_indicator_name = 'FIB_RETRACEMENT_' + str_col_name + str(int_period) + '_'
            
            for ratio in lst_ratios:
                str_indicator_name_new = str_indicator_name + str(ratio)
                self.__df_data[str_indicator_name_new] = pdu.optimize_mem_usage(
                                                                    max_price - (diff * ratio))
                self.__lst_indicator_names.append(str_indicator_name_new)
            
            return True
        except:
            return False

    def reset_data(self):
        try:
            self.__df_data.drop(self.__lst_indicator_names, axis=1, inplace=True)
            return True
        except:
            return False
        
    def undo_last(self, int_num_to_undo = 1):
        try:
            if int_num_to_undo == 1:
                self.__df_data.drop(self.__lst_indicator_names[-1], axis=1, inplace=True)
            else:
                self.__df_data.drop(self.__lst_indicator_names[-int_num_to_undo:-1], axis=1, inplace=True)
            return True
        except:
            return False
        
        
if __name__ == '__main__':
    
    import sys
    sys.path.append("\\Dropbox\\Yuan Qing\\Work\\Projects\\Libraries\\3. Python\\1. Modules\\mod\\")
    import modYahooData3 as yh
    import modTechnicalAnalysis3 as ta
    
    ticker = "GLE.PA"
    csv_path = "..\\..\\2. Notebooks\\1. Data"
    start_date = "26 Jan 2018"
    end_date = "18 Jan 2019"
    
    data_object = yh.YahooData(ticker, start_date, end_date, None, csv_path)
    df = data_object.get_data()
    obj_ta = ta.TechnicalAnalysis(df)

    num_of_multiples = 5
    step = 7
    for x in range(step,step * (num_of_multiples+1), step):
        obj_ta.gen_rsi('Adj Close', x)
    
    periods = [50, 100, 200]
    for period in periods:
        obj_ta.gen_ma('Adj Close',period,ta.ENUM_MA_METHOD.SMA)
        
    obj_ta.gen_crossover('SMA_Adj Close_200', 'SMA_Adj Close_50')
    print(obj_ta.get_data().head())
    