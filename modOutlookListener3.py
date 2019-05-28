# -*- coding: utf-8 -*-
"""
Created on Sat Mar 18 11:04:12 2017

@author: Lim Yuan Qing
"""

strModPath = r'C:/Users/yuanq/Dropbox/Yuan Qing/Work/Projects/1. Libraries/3. Python/Modules/mod/'
strDBFilePath = r''
strUser = ''
strPassword = ''

import sys
sys.path.append(strModPath)
import modFunctions as fnc
import modDatabaseFunctions as dbfnc

from bs4 import BeautifulSoup as bs
import win32com.client
import pythoncom
import dateutil.parser
import re


# https://stackoverflow.com/questions/49695160/how-to-continuously-monitor-a-new-mail-in-outlook-and-unread-mails-of-a-specific
class Handler_Class(object):    
    
    def OnNewMailEx(self, receivedItemsIDs): 
        for ID in receivedItemsIDs.split(','):
            # Microsoft.Office.Interop.Outlook_MailItem properties
            # https://msdn.microsoft.com/en-us/library/microsoft.office.interop.outlook._mailitem_properties.aspx
            msg = outlook.Session.GetItemFromID(ID)
            if msg.Class == 43:
                dictBasicEmailDetails = self.fnc_DictBasicEmailDetails(msg)
                print(dictBasicEmailDetails['From'])
#                if fnc.fnc_InStr('GMIM', dictBasicEmailDetails['Subject'],False) and fnc.fnc_InStr('SG-PBEquitiesDesk@uobgroup.com', dictBasicEmailDetails['From'],False):
#                    objConn = dbfnc.fnc_StartConn(strDBFilePath, strUser, strPassword)
#                    objCur = objConn.cursor()
#                    objCur.execute("INSERT INTO tblClientEmail ([ConvoID], [ConvoInd], [ConvoTop], [Subject], [From], [To], [Cc], [HTMLBody], [RecTime], [SavePath], [Status]) VALUES ('" + 
#                            dictBasicEmailDetails['ConversationID'] +
#                            "','" + dictBasicEmailDetails['ConversationIndex'] +
#                            "','" + dictBasicEmailDetails['ConversationTopic'] +
#                            "','" + dictBasicEmailDetails['Subject'] +
#                            "','" + dictBasicEmailDetails['From'] +
#                            "','" + dictBasicEmailDetails['To'] +
#                            "','" + dictBasicEmailDetails['Cc'] +
#                            "','" + dictBasicEmailDetails['HTMLBody'].replace("'","''") +
#                            "','" + dictBasicEmailDetails['ReceivedOn'].strftime('%d/%m/%Y %T') +
#                            "','', 'Received')")
#                    objConn.commit()
#                    objConn.close()  

    def OnItemAdd(self, objMailItem):
        pass
                                    
    def fnc_EmailRecipientNamesToAddresses(self, strEmailNames, objMailItem):
        dictEmailAddresses = dict()
        strOutput = ''
        dictEmailAddresses = self.fnc_GetDictOfAllRecipientsSMTPMailAddresses(objMailItem)
        vTemp = strEmailNames.split('; ')
        for vName in vTemp:
            if vName.strip() != '':
                strOutput = strOutput + str(dictEmailAddresses[vName]) + '; '        
        return strOutput.strip()
    
    def fnc_GetSenderSMTPMailAddress(self, objMailItem):        
        objReply = objMailItem.Reply()
        objRecipient = objReply.Recipients[1]
        strAddress = objRecipient.PropertyAccessor.GetProperty(r'http://schemas.microsoft.com/mapi/proptag/0x39FE001E').strip()                
        return strAddress
    
    def fnc_GetDictOfAllRecipientsSMTPMailAddresses(self, objMailItem):
        dictOutputs = dict()
        for objRecipient in objMailItem.Recipients:
            dictOutputs[objRecipient.Name] = objRecipient.PropertyAccessor.GetProperty(r'http://schemas.microsoft.com/mapi/proptag/0x39FE001E').strip()
        return dictOutputs
    
    def fnc_GetRealAttachmentCount(self, objMailItem):
        i = 0
        for objAttachment in objMailItem.Attachments:
            strCID = objAttachment.PropertyAccessor.GetProperty(r'http://schemas.microsoft.com/mapi/proptag/0x3712001E')
            if strCID == '':
                i = i + 1
        return i
                                   
    def fnc_DictBasicEmailDetails(self, objMailItem):
        dictBasicEmailDetails = dict()
        dictBasicEmailDetails['To'] = self.fnc_EmailRecipientNamesToAddresses(objMailItem.To, objMailItem)
        dictBasicEmailDetails['From'] = self.fnc_GetSenderSMTPMailAddress(objMailItem)
        dictBasicEmailDetails['Cc'] = self.fnc_EmailRecipientNamesToAddresses(objMailItem.CC, objMailItem)
        dictBasicEmailDetails['Subject'] = objMailItem.Subject
        dictBasicEmailDetails['ConversationID'] = objMailItem.ConversationID
        dictBasicEmailDetails['ConversationIndex'] = objMailItem.ConversationIndex                     
        dictBasicEmailDetails['ConversationTopic'] = objMailItem.ConversationTopic
        dictBasicEmailDetails['Body'] = re.sub(r'\r\n', ' ', objMailItem.Body)
        dictBasicEmailDetails['HTMLBody'] = objMailItem.HTMLBody
        dictBasicEmailDetails['SentOn'] = objMailItem.SentOn
        dictBasicEmailDetails['ReceivedOn'] = objMailItem.ReceivedTime
        dictBasicEmailDetails['Attachment'] = (self.fnc_GetRealAttachmentCount(objMailItem) > 0)
        return dictBasicEmailDetails

def fnc_HTMLToTables(strHTML):
    """Extracts tables from html body of Outlook email"""
    objHTML = bs(strHTML, 'lxml')
    objTables = objHTML.findAll('table')
    arrTable = []
    for objTable in objTables:
        arrRow = []
        for objRow in objTable.findAll('tr'):
            arrCol = []
            for objCol in objRow.findAll('td'):
                arrCol.append(objCol.get_text().strip())                
            arrRow.append(arrCol)            
        arrTable.append(arrRow)    
    return arrTable

def fnc_TableToHTML(lst_table, 
                    bln_header = True):
    str_html = '<table style="width:100%; border-collapse:collapse;", border=1>'
    first_row = 0
    if bln_header:
        str_html = str_html + '<tr>'
        for i in range(len(lst_table[0])):
            str_html = str_html + '<th>' + str(lst_table[0][i]) + '</th>'
        str_html = str_html + '</tr>'
        first_row = 1
    
    for i in range(first_row, len(lst_table)):
        str_html = str_html + '<tr>'
        for j in range(len(lst_table[i])):
            str_html = str_html + '<td>' + str(lst_table[i][j]) + '</td>'
            
        str_html = str_html + '</tr>'
        
    str_html = str_html + '</table>'
    return str_html
    

def fnc_ReadRules():
    """Read rules from Outlook folder"""
    objOutlook = win32com.client.Dispatch('Outlook.Application').GetNamespace('MAPI')
    objInbox = objOutlook.GetDefaultFolder(6)
    objRules = objInbox.Parent.Folders.Item('Rules')
    dictMails = dict()
    for objMail in objRules.Items:
        arrTables = fnc_HTMLToTables(objMail.HTMLBody)
        arrTable = arrTables[0]
        dictRules = dict()
        for i in range(len(arrTable)-1):
            dictHeaders = dict()
            for j in range(len(arrTable[i])):
                dictValues = dict()
                for strVal in (arrTable[i+1][j].strip().split('|')):
                    dictValues[strVal.strip()] = strVal.strip()                    
                dictHeaders[arrTable[0][j].strip()] = dictValues                            
            dictRules[i+1] = dictHeaders                     
        dictMails[objMail.Subject] = dictRules            
    return dictMails

def fnc_ReadTextRules(strTextFilePath):    
    # Settings
    strFilePath = strTextFilePath
    # List of allowed conditions to allow for future additions without having to
    # change the code
    lstConditions = ['FROM', 'TO', 'CC', 'SUBJECT']
    
    # dicReturn is the dictionary to return from this function {'A':dicActions}
    dicReturn = dict()
    
    # dicConditions is a dictionary of dictionaries - each sub dictionary represents
    # 1 condition from lstConditions {condition:{toMatch:ruleNum}}
    # e.g. {FROM:{LIM.YUANQING@UOBGROUP.COM:1}}
    dicConditions = dict()
    
    for condition in lstConditions:
        dicConditions[condition] = dict()
        
    # dicActions is a dictionary of strings {ruleNum:action}
    dicActions = dict()
    
class Rule():
    def __init__(self, lst_subject, 
                 str_from = None, 
                 lst_to = None, 
                 lst_cc = None):
        self.__lst_subject = lst_subject
        self.__str_from = str_from
        self.__lst_to = lst_to
        self.__lst_cc = lst_cc
    
    def __del__(self):
        pass
    
    def __len__(self):
        pass
    
    def __repr__(self):
        pass
    
    def check_rule(self, dic_basic_email_details):
        self.__is_true = bool(re.findall(lst_subject, 
                                         dic_basic_email_details['Subject']))
        if not self.__str_from:
            self.__is_true = (self.__is_true and 
                              bool(re.findall(self.__str_from, 
                                              dic_basic_email_details['From'])))
        
        
                              
        pass
    
    

if __name__ == '__main__':
    outlook = win32com.client.DispatchWithEvents('Outlook.Application', Handler_Class)
    pythoncom.PumpMessages()
    
                