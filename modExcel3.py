# -*- coding: utf-8 -*-
"""
Created on Fri Jun 16 21:45:01 2017

@author: Lim Yuan Qing
"""

import xlwings as xw
from xlwings.constants import Direction
from collections import defaultdict
import pandas as pd

class StaticData:
    dictStatic = dict()
    def __init__(self, strWorkbookPath, strStaticSheetName):
        self.__p_strWorkbookPath = strWorkbookPath
        self.__p_strStaticSheetName = strStaticSheetName
        self.__p_wbStatic = None
        
    def getWorkbook(self):
        return self.__p_wbStatic
        
    def getWorkbookPath(self):
        return self.__p_strWorkbookPath
    
    def setWorkbookPath(self, strWorkbookPath):
        self.__p_strWorkbookPath = strWorkbookPath
        return None
    
    def getStaticSheetName(self):
        return self.__p_strStaticSheetName
    
    def setStaticSheetName(self, strStaticSheetName):
        self.__p_strStaticSheetName = strStaticSheetName
        return None
    
    def readStatic(self):
        intWsNameLen = len(self.__p_strStaticSheetName)        
        
        self.__p_wbStatic = xw.Book(self.__p_strWorkbookPath)        
        shtStatic = self.__p_wbStatic.sheets[self.__p_strStaticSheetName]
        
        speedXlwingsBook(self.__p_wbStatic,False,False,False)
        
        for nmeRange in self.__p_wbStatic.names:            
            if nmeRange.name[0:intWsNameLen] == self.__p_strStaticSheetName:
                strRangeName = nmeRange.name[-(len(nmeRange.name)-intWsNameLen-1):]
                if shtStatic.range(strRangeName).offset(1,0).value:
                    strDataStruc = strRangeName[0:3]
                    if strDataStruc == 'dic':
                        tempRange = shtStatic.range(strRangeName).expand('table')
                        dictTemp = listToDict(tempRange.value)
                    elif strDataStruc == 'tbl':
                        tempRange = shtStatic.range(strRangeName).expand('table')                        
                        dictTemp = tableToDict(tempRange.value)
                    elif strDataStruc == 'lst':
                        tempRange = shtStatic.range(strRangeName).expand('down')
                        dictTemp = listToDict(tempRange.value)
                    elif strDataStruc == 'lts':
                        lngMaxRow = max(
                                [shtStatic.range(rngCell).expand('down').rows.count
                                 for rngCell in shtStatic.range(strRangeName).expand('right')]
                                )
                        tempRange = shtStatic.range(
                                shtStatic.range(strRangeName).end(Direction.xlToRight),
                                shtStatic.range(strRangeName).offset(lngMaxRow-1,0)                                
                                )
                        dictTemp = multiListToDict(tempRange.value)
                    else:
                        pass
                    
                    self.dictStatic[strRangeName[3:]] = dictTemp
            
        speedXlwingsBook(self.__p_wbStatic)
        return self.dictStatic
                    

def listToDict(lstInputs):
    dictOutput= dict()
    rows = len(lstInputs)
    cols = len(lstInputs[0])
    
    if rows == 2:
        for x in range(cols):
            dictOutput[str(lstInputs[0][x]).strip()] = str(lstInputs[1][x]).strip()
    elif cols == 2:
        for x in range(rows):
            dictOutput[str(lstInputs[x][0]).strip()] = str(lstInputs[x][1]).strip()
    else:
        pass
    
    return dictOutput

def tableToDict(tableInputs):
    dictOutput = defaultdict(list)
    lstKeyValue = [(str(tableInputs[x][0]).strip() + str(tableInputs[0][y]).strip(), 
                    str(tableInputs[x][y]).strip()) 
                    for x in range(len(tableInputs)) 
                    for y in range(len(tableInputs[0]))
                    ]
    for k, v in lstKeyValue:
        dictOutput[k].append(v)
    dictOutput.default_factory = None
    return dictOutput

def multiListToDict(multiListInputs):
    return {k:v for k,v in
                [(str(multiListInputs[0][y]).strip(), listToDict([multiListInputs[x][y] 
                for x in range(len(multiListInputs))])) 
                for y in range(len(multiListInputs[0]))                
                ]
            }          

def speedXlwingsBook(book, autoCalculate = True, screenUpdating = True, displayAlerts = True):
    if autoCalculate:
        book.app.calculate = r'automatic'
    else:
        book.app.calculate = r'manual'
        
    book.app.screen_updating = screenUpdating
    book.app.display_alerts = displayAlerts

def getRange(rngStart, dirOne = None, dirTwo = None):
    if dirTwo is None:
        return rngStart.expand(dirOne)
    else:
        return rngStart.expand(dirOne).expand(dirTwo)

if __name__ == '__main__':
#    static = StaticData(r'C:\Users\Lim Yuan Qing\Desktop\classDataTest.xlsm', 'Static')
#    static.readStatic()
    df = pd.read_csv(r'C:\Users\Lim Yuan Qing\AppData\Roaming\MetaQuotes\Terminal\1DAFD9A7C67DC84FE37EAA1FC1E5CF75\MQL4\Files\Daily_Base.csv')
    
    
    