# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 23:47:40 2019

@author: LIM YUAN QING
"""

from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from win32api import GetUserName
import struct
import pathlib

def get_installed_distributions():
    try:
        from pip._internal.utils.misc import get_installed_distributions
    except ImportError:  # pip<10
        from pip import get_installed_distributions
    else:
        print('pip not found')

    return sorted(["%s==%s" % (i.key, i.version)
                   for i in get_installed_distributions()])
    
def file_exists(str_file_path):
    path = pathlib.Path(str_file_path)
    if path.is_file():
        return True
    else:
        return False

def directory_exists(str_directory_path):
    path = pathlib.Path(str_directory_path)
    if path.is_dir():
        return True
    else:
        return False

def get_user_name():
    return GetUserName()

def gen_date(date, relative_days=0, relative_months=0, relative_years=0):
    return parse(date) + relativedelta(years=relative_years, 
                                        months=relative_months, 
                                        days = relative_days)

def get_sys_bit():
    return 8 * struct.calcsize("P")

def is_32_bit():
    return get_sys_bit() == 32

def is_64_bit():
    return get_sys_bit() == 64
    
def is_date(str_date):
    """
    Check if string is date.
    
    Parameters
    ----------
    str_date : string
        string to check
    
    Returns
    -------
    boolean
        True if string is possibly a date
    """
    try:
        parse(str_date)
        return True
    except ValueError:
        return False
    
def merge_dicts(*args):
    """
    Merge n dictionaries.
    
    Parameters
    ----------
    *args : dictionary
        variable arguments of dictionary type to be merged into 1 dictionary
        
    Returns
    -------
    dictionary
        dictionary that is the result of merging input dictionaries
    """
    combined = dict()
    for dictionary in args:
        combined.update(dictionary)
    return combined

if __name__ == '__main__':
    print(get_installed_distributions())