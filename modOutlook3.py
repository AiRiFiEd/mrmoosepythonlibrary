# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 14:34:16 2019

@author: yuanq
"""

import win32com.client
import logging
import modUtils3 as util

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

str_format = '%(asctime)s:%(levelname)s:%(message)s'
formatter = logging.Formatter(str_format)

file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

def send_email(str_to, 
               str_cc, 
               str_bcc, 
               str_subject, 
               str_body, 
               bln_send = False, 
               dte_delay = None, 
               str_mailbox_to_use = None, 
               lst_attachment_paths = None):
    outlook = win32com.client.DispatchEx('Outlook.Application')
    if str_mailbox_to_use:
        namespace = outlook.GetNamespace('MAPI')
        recipient = namespace.CreateRecipient(str_mailbox_to_use)
        recipient.Resolve()
        try:
            folder = namespace.Folders[str_mailbox_to_use].Folders["Inbox"]
        except:
            logger.error('Mailbox not found.')
            return False
        if not folder:
            logger.error('Inbox not found in specified mailbox.')
            return False
        mail_item = folder.Items.Add()
    else:
        mail_item = outlook.CreateItem(0)
    mail_item.To = str_to
    mail_item.CC = str_cc
    mail_item.BCC = str_bcc
    mail_item.Subject = str_subject
    if '<html>' in str_body.lower():
        mail_item.HTMLBody = str_body
    else:
        mail_item.Body = str_body
    if lst_attachment_paths:
        for attachment in lst_attachment_paths:
            if util.file_exists(attachment):
                mail_item.Attachments.Add(attachment)
            else:
                logger.info(str(attachment) + ' does not exist.')
    if dte_delay:
        mail_item.DeferredDeliveryTime = dte_delay
    if bln_send:
        mail_item.Send()
    else:
        mail_item.Display()
    return True

if __name__ == '__main__':                                  
#    status = send_email('yuanqing87@gmail.com',
#                        '',
#                        '',
#                        'Test',
#                        'This is a test email.',
#                        False,
#                        util.gen_date('30 Apr 2019',2),
#                        'asda',
#                        ['C:\\Users\\yuanq\\Dropbox\\Yuan Qing\\Work\\Projects\\Libraries\\3. Python\\1. Modules\\mod\\careers.py'])
#    print(status)
    print(util.get_installed_distributions())