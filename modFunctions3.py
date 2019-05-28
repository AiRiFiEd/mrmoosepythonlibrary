# -*- coding: utf-8 -*-
"""
Created on Wed Mar 22 19:48:16 2017

@author: Lim Yuan Qing
"""

strModPath = r'C:/Users/yuanq/Dropbox/Yuan Qing/Work/Projects/1. Libraries/3. Python/Modules/mod/'

import sys
sys.path.append(strModPath)
import win32com.client
import pandas as pd
import cchardet
import zipfile
import os

def get_filepaths(str_directory):
    return [os.path.abspath(file) for file in os.listdir(str_directory)]

def zip_file(str_zip_full_path, str_file_full_path):
    try:
        str_zip_full_path_new = str_zip_full_path + ('.zip' not in str_zip_full_path) * '.zip'
        obj_zipfile = zipfile.ZipFile(str_zip_full_path_new, 'a', zipfile.ZZIP_DEFLATED)
        obj_zipfile.write(str_file_full_path, str_file_full_path.split('\\')[-1])
        obj_zipfile.close()
        return True
    except:
        return False

def pandasDFToExcel(df, strFilePath, strSheet, blnHeader, blnIndex):
    """Saves Pandas dataframe to excel"""
    strFilePath = str(strFilePath)
    strSheet = str(strSheet)
    if os.path.exists(strFilePath):
        objExcel = win32com.client.DispatchEx('Excel.Application')
        objWb = objExcel.Workbooks.Open(Filename = strFilePath)
        objWb.Sheets(strSheet).Cells.ClearContents()
        objWb.Save()
        objExcel.Quit()
        del objExcel
        
    objExcel = pd.ExcelWriter(strFilePath)
    df.to_excel(objExcel, strSheet, header = blnHeader, index = blnIndex)
    objExcel.save()
    del objExcel

def inStr(strSubString, strFullString, blnCaseSensitive):
    if blnCaseSensitive:
        return (str(strSubString) in str(strFullString))
    else:
        return (str(strSubString).upper() in str(strFullString).upper())
    
def inStrMulti(lstSubStrings, strFullString, blnCaseSensitive):
    if blnCaseSensitive:
        return any(str(subString) in str(strFullString) for subString in lstSubStrings)
    else:
        return any(str(subString).upper() in str(strFullString).upper() for subString in lstSubStrings)
        
def isNumeric(string):
    try:
        float(string)
        return True
    except ValueError:
        return False
    
def fibonacciNumber(n):
    dic = {}
    for i in range(1, n+1):
        if i == 1 or i ==2:
            dic[i] = 1
        else:
            dic[i] = dic[i-1] + dic[i-2]
            
    return dic[n]

def convertEncoding(data, newCoding = 'UTF-8'):
    encoding = cchardet.detect(data)['encoding']
    if newCoding.upper() != encoding.upper():
        data = data.decode(encoding, data).encode(newCoding)
        
    return data
    
if __name__ == '__main__':
    pass