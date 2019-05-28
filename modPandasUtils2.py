# -*- coding: utf-8 -*-
"""
Created on Sat Dec 22 15:10:53 2018

@author: LIM YUAN QING
"""

import pandas as pd
import numpy as np

def optimize_mem_usage(pd_input, display = False):
    '''
    Optimize memory usage of pandas DataFrame and Series.
    
    Parameters
    ----------
    pd_input : pandas DataFrame or Series object
        a pandas data structure.
    display : bool, optional
        True to print memory usage of `pd_input` before and after optimization
        (the default is False - function will not print the memory usage of 
        `pd_input` before and after optimization)        
    
    Returns
    -------
    pandas object
        a pandas object of the same type as the input `pd_input` 
    
    Notes
    -----
    Determines data type of inputs and choose smallest possible data type to
    downcast them. If data type is non-numeric and less than or equal to 50% of
    the input data are unique, they will be stored as pandas categorical type.    
    
    References
    ----------
    [1] https://www.dataquest.io/blog/pandas-big-data/
    [2] https://www.kaggle.com/arjanso/reducing-dataframe-memory-size-by-65
    '''
    assert isinstance(pd_input, pd.DataFrame) or isinstance(pd_input, pd.Series), 'pd_data is neither a pandas DataFrame nor Series object'
    
    input_type = pd_input.dtype
    before = ['Before', input_type, mem_usage(pd_input)]    
    if input_type == np.int64:
        if is_categorical(pd_input):
            pd_input.astype('category')
        else:
            if pd_input.min() < 0:
                output = pd.to_numeric(pd_input,downcast='signed')
            else:
                output = pd.to_numeric(pd_input,downcast='unsigned')      
    elif input_type == np.float64:
        output = pd.to_numeric(pd_input,downcast='float')               
    elif input_type == np.object:
        try:
            output = pd.to_datetime(pd_input)
        except:            
            if unique_ratio(pd_input) <= 0.5:
                output = pd_input.astype('category')
            else:
                output = pd_input
    else:
        output = pd_input
    
    after = ['After', output.dtype, mem_usage(output)]
    report = [before, after]
    if display:
        print pd.DataFrame(report,columns=[pd_input.name, 'Data Type', 'Size (MB)']).set_index(pd_input.name)
        
    return output
    
def mem_usage(pd_input):
    if isinstance(pd_input, pd.DataFrame):
        usage_b = pd_input.memory_usage(deep=True).sum()
    else:
        usage_b = pd_input.memory_usage(deep=True)
    
    usage_mb = usage_b/1024.0 **2.0
    return '{:03.2f} MB'.format(usage_mb)

def unique_ratio(data):
    return 1.0*data.nunique()/data.count()

def unique_top_freq(data, top_n):
    return (1.*data.value_counts(normalize=True).head(top_n)).sum()
    
def is_categorical(data, unique_threshold=0.05, unique_top_threshold = 0.90, top_n = -1):
    if top_n == -1:
        top_n_new = int(round((1-unique_top_threshold) * (1.*data.value_counts(normalize=True).head(3)).shape[0]))
    else:
        top_n_new = top_n
        
    return (unique_ratio(data) <= unique_threshold and 
            unique_top_freq(data, top_n_new) >= unique_top_threshold)