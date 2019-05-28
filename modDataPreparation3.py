# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 14:19:42 2018

@author: LIM YUAN QING
"""

# Road map
# --------
# 1. Determine if variables are of numeric or non-numeric types
# 2. For numeric data types, determine if variable is categorical or continuous
# 3. Descriptive statistics
# 4. Optimise memory usage

import pandas as pd
import enum
from enum import Enum
import modPandasUtils3 as pdu
import modUtils3 as utils
import multiprocessing as mp
#from sklearn.model_selection import RepeatedStratifiedKFold

@enum.unique
class ENUM_DATA_SET_TYPE(Enum):
    CROSS_SECTIONAL = 1
    TIME_SERIES = 2
    
@enum.unique
class ENUM_DATA_TYPE(Enum):
    CONTINUOUS = 1
    CATEGORICAL = 2
    FREE_TEXT = 3

class DataPreparation():
    '''
    
    
    
    
    
    '''
    def __init__(self, X, y, data_type = ENUM_DATA_SET_TYPE.CROSS_SECTIONAL):
        assert isinstance(X, pd.DataFrame), "X is not a pandas DataFrame"
        assert isinstance(y, pd.DataFrame), "y is not a pandas DataFrame"
        assert len(X.index) == len(y.index), "X and y have different number of rows"
        assert y.shape[1] == 1, "y should have 1 column only"

        self.__df_X = X.copy()
        self.__df_y = y.copy()
        
        print('OPTIMIZING DATA USAGE - START')
        pool = mp.Pool(processes = mp.cpu_count()-1)
        results = [pool.apply(pdu.optimize_mem_usage, args=(X[var],True)) 
                    for var in X.columns]
        for col in results:
            self.__df_X[col.name] = col
            
        results = [pool.apply(pdu.optimize_mem_usage, args=(y[var],)) 
                    for var in y.columns]
        for col in results:
            self.__df_y[col.name] = col
            
        pool.close()
        print('OPTIMIZING DATA USAGE - END')
        #self.__dict_dtypes = self.__df_X.dtypes.to_dict()
        self.__dict_dtypes = utils.merge_dicts(self.__df_X.dtypes.to_dict(),
                                               self.__df_y.dtypes.to_dict())
        
#        self.__dic_dtypes = dict()
#        
#        for var in lst_numeric_X:
#            if pdu.is_categorical(X[var]):
#                self.__dic_dtypes[var] = ENUM_DATA_TYPE.CATEGORICAL
#            else:
#                self.__dic_dtypes[var] = ENUM_DATA_TYPE.CONTINUOUS
#        
#        for var in lst_non_numeric_X:
#            self.__dic_dtypes[var] = ENUM_DATA_TYPE.CATEGORICAL
#            
#        for var in y.columns:
#            if pd.api.types.is_numeric_dtype(y[var]):
#                if pdu.is_categorical(y[var]):
#                    self.__dic_dtypes[var] = ENUM_DATA_TYPE.CATEGORICAL
#                else:
#                    self.__dic_dtypes[var] = ENUM_DATA_TYPE.CONTINUOUS
#            else:
#                self.__dic_dtypes[var] = ENUM_DATA_TYPE.CATEGORICAL    
    def __del__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
#    def get_data_type_dictionary(self):
#        return self.__dic_dtypes
#    
#    def set_data_type(self, col_name, enum_data_type):
#        if col_name in self.__dic_dtypes:
#            self.__dic_dtypes[col_name] = enum_data_type
#            return True
#        else:
#            return False
#    
#    def impute_missing_values(self):
#        pass
#    
#    def gen_train_test(self, n_splits = 5, n_repeats=20, random_state=None):
#        #rskf = RepeatedStratifiedKFold(n_splits=n_splits, n_repeats=n_repeats, random_state=random_state)
#        pass
    
    
    
if __name__ == '__main__':
    data = pd.read_csv(r"..\\..\\..\\99. Datasets\\kuc-hackathon-winter-2018\\drugsComTrain_raw.csv")
    df_rating = pd.DataFrame(data['rating'])
    df_X = data[['uniqueID', 'drugName','condition','review','date','usefulCount']]

    dp = DataPreparation(df_X, df_rating)

    data_types = dp._DataPreparation__dict_dtypes
    categorical = data_types['drugName']
    print(type(categorical) )
 