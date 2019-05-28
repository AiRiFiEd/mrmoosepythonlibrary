# -*- coding: utf-8 -*-
"""
Created on Mon Dec 31 19:07:19 2018

@author: yuanq
"""

import blpapi
from optparse import OptionParser
import enum
import modUtils3 as util
from operator import itemgetter

DATE = blpapi.Name('date')
SECURITY_DATA = blpapi.Name('securityData')
SECURITY = blpapi.Name('security')
FIELD_DATA = blpapi.Name('fieldData')
FIELD_EXCEPTIONS = blpapi.Name('fieldExceptions')
FIELD_ID = blpapi.Name('fieldId')
ERROR_INFO = blpapi.Name('errorInfo')
ASSET_CLASS = ['EQUITY', 'COMDTY', 'INDEX', 'CURNCY']

@enum.unique
class ENUM_DATA_REQUEST_TYPES(enum.Enum):
    STREAMING = 1
    PER_REQUEST = 2
    HISTORICAL = 3
    INTRADAY = 4

def process_inputs(inputs):
    """
    Helper function to convert `inputs` to a list of upper-case strings.
    
    Parameters
    ----------
    inputs : 
    """
    bln_is_list = isinstance(inputs, list)
    if bln_is_list:
        return [inp.upper() for inp in inputs]
    else:
        return [inputs.upper()]
   
def supported_assets(lst_security, 
                     bln_return_unsupported = False):
    lst_security_new = [sec.upper() for sec in lst_security 
                        if sec.upper().split()[-1] in ASSET_CLASS]
    if len(lst_security) != len(lst_security_new):
        set_security_new = set(lst_security_new)
        lst_unsupported = [unsupported for unsupported in lst_security 
                           if unsupported not in set_security_new]
        if bln_return_unsupported:
            return lst_unsupported
        else:
            print(lst_unsupported)
            return lst_security_new
    else:
        return lst_security_new

def bloomberg_bdp(security, field, *args):
    """
    Equivalent to Bloomberg Excel BDP function.
    
    Parameters
    ----------
    security : string
        Bloomberg identifier (e.g. '700 HK EQUITY')
    field : string
        Bloomberg field (e.g. 'PX_LAST')
    *args : variable length argument list of strings, optional
        contains overrides (e.g. 'field_id=value')
        
    Returns
    -------
    string
        value for the requested field
        
    References
    ----------
    [1] https://www.bloomberg.com/professional/support/api-library/
    
    """
    security_new = supported_assets(process_inputs(security))
    field_new = process_inputs(field)
    
    bloomberg_data = gen_bloomberg_data(security_new, field_new, args)
    return [[bloomberg_data[sec][fld] if fld in bloomberg_data[sec] else ''
             for fld in field_new] 
            for sec in security_new]

def bloomberg_bds(security, field, *args):
    """
    Equivalent to Bloomberg Excel BDS function.
    
    Parameters
    ----------
    security : string
        Bloomberg identifier (e.g. '700 HK EQUITY')
    field : string
        Bloomberg field (e.g. 'PX_LAST')
    *args : variable length argument list of strings, optional
        contains overrides (e.g. 'field_id=value')
        
    Returns
    -------
    list
        values for the requested field
        
    References
    ----------
    [1] https://www.bloomberg.com/professional/support/api-library/
    
    """ 
    security_new = supported_assets(process_inputs(security))
    field_new = process_inputs(field)
    
    bloomberg_data = gen_bloomberg_data(security_new, field_new, args)
    return [[sorted([[val for val in item.split('|')] 
                      for item in list(bloomberg_data[sec][fld].keys())], key = itemgetter(0)) 
                         for fld in field_new]
                             for sec in security_new]
    
def bloomberg_bdh(security, field, start_date, end_date, *args):
    """
    Equivalent to Bloomberg Excel BDH function.
    
    Parameters
    ----------
    security : string
        Bloomberg identifier (e.g. '700 HK EQUITY')
    field : string
        Bloomberg field (e.g. 'PX_LAST')
    start_date : string
        data start date in the format of 'yyyymmdd' (e.g. '20181228')
    end_date : string
        data end date in the format of 'yyyymmdd' (e.g. '20181228')        
    *args : variable length argument list of strings, optional
        contains overrides (e.g. 'field_id=value')
        
    Returns
    -------
    list
        nested list of [date, value] pairs sorted by date in ascending order
        
    References
    ----------
    [1] https://www.bloomberg.com/professional/support/api-library/
    
    """ 
    security_new = supported_assets(process_inputs(security))
    field_new = process_inputs(field)
    
    if '=' in start_date:
        start_date_new = start_date.split('=')[1]
    else:
        start_date_new = start_date
        
    if '=' in end_date:
        end_date_new = end_date.split('=')[1]
    else:
        end_date_new = end_date
        
    assert util.is_date(start_date_new), 'Invalid start date.'
    assert util.is_date(end_date_new), 'Invalid end date.'
    
    bloomberg_data = gen_bloomberg_data(security_new, field_new, start_date_new, end_date_new, args, ENUM_DATA_REQUEST_TYPES.HISTORICAL)
    
    data = [[[[dte, bloomberg_data[sec][fld][dte]] 
                for dte in sorted(list(bloomberg_data[sec][fld].keys()))] 
                    for fld in field_new]
                        for sec in security_new]
    return data

def gen_bloomberg_data(security, field, overrides = None, start_date = None, 
                       end_date = None, enum_data_request_type = ENUM_DATA_REQUEST_TYPES.PER_REQUEST):
    if overrides:
        lst_overrides = [override for override in overrides]
    else:
        lst_overrides = None
        
    obj_bloomberg_data = BloombergDataSync(security, field, start_date, end_date, 
                                           lst_overrides, enum_data_request_type)
    return obj_bloomberg_data.get_data()

#def is_supported_asset(security):
#    security_new = security.upper()
#    if not security_new.split()[-1] in ASSET_CLASS:
#        return False
#    else:
#        return True
    
class BloombergDataSync():
    def __init__(self, lst_securities, lst_fields, start_date = None, end_date = None,
                 lst_overrides = None, 
                 enum_data_request_type = ENUM_DATA_REQUEST_TYPES.PER_REQUEST):
        self.__enum_data_request_type = enum_data_request_type
        if isinstance(lst_securities, list):
            self.__lst_securities = lst_securities
        else:
            self.__lst_securities = [lst_securities]
            
        if isinstance(lst_fields, list):
            self.__lst_fields = lst_fields
        else:
            self.__lst_fields = [lst_fields]
            
        if lst_overrides is None:
            self.__lst_overrides = None
        elif isinstance(lst_overrides, list):
            self.__lst_overrides = list(lst_overrides)
        else:
            self.__lst_overrides = [lst_overrides]
            
        self.__dic_data = dict()
        options = self.parseCmdLine()
        
        # Fill SessionOptions
        session_options = blpapi.SessionOptions()
        session_options.setServerHost(options.host)
        session_options.setServerPort(options.port)
        
        print('Connecting to %s:%d' % (options.host, options.port))
        
        # Create a Session
        session = blpapi.Session(session_options)
        
        # Start a Session
        if not session.start():
            print('Failed to start session...')
            return
        else:
            print('Session started.')
            
        service_name = self.get_service()
        
        if not session.openService(service_name):
            print('Failed to open ' + service_name)
            return
        else:
            print(service_name + ' opened.')
            
        data_service = session.getService(service_name)
        request = data_service.createRequest(self.get_request())
        
        for security in self.__lst_securities:
            request.append('securities', security)
            
        for field in self.__lst_fields:
            request.append('fields', field)
            
        if not self.__lst_overrides is None:
            overrides = request.getElement('overrides')
            for override in self.__lst_overrides:
                if '=' in override:
                    temp = override.split('=')
                    field_id = temp[0]
                    value = temp[1]
                    override_element = overrides.appendElement()
                    override_element.setElement('fieldId', field_id)
                    override_element.setElement('value', value)
                else:
                    request.append('fields', override)
                    
        if self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.HISTORICAL:
            request.set('startDate', start_date)
            request.set('endDate', end_date)
            if start_date:
                request.set('startDate', start_date)
            if end_date:
                request.set('endDate', end_date)
                
        session.sendRequest(request)
        try:
            while(True):
                event = session.nextEvent(500)
                if (event.eventType() == blpapi.Event.RESPONSE or 
                    event.eventType() == blpapi.Event.PARTIAL_RESPONSE):
                    for msg in event:
                        #self.__dic_data = self.process_message(msg)
                        self.process_message(msg)
                        
                if event.eventType() == blpapi.Event.RESPONSE:
                    break
        finally:
            session.stop()
                    

    def __del__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def get_data(self):
        return self.__dic_data
    
    def get_service(self):
        if self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.PER_REQUEST:
            return '//blp/refdata'
        elif self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.HISTORICAL:
            return '//blp/refdata'
        elif self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.STREAMING:
            return '//blp/mktdata'
        
    def get_request(self):
        if self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.PER_REQUEST:
            return 'ReferenceDataRequest'
        elif self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.HISTORICAL:
            return 'HistoricalDataRequest'
        elif self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.STREAMING:
            return ''
        
    def get_data_request_type(self):
        return self.__enum_data_request_type
    
    def set_data_request_type(self, enum_data_request_type):
        self.__enum_data_request_type = enum_data_request_type
    
    def parseCmdLine(self):
        parser = OptionParser(description='Retrieve reference data.')
        parser.add_option('-a',
                          '--ip',
                          dest='host',
                          help='server name or IP (default: %default)',
                          metavar='ipAddress',
                          default='localhost')
        parser.add_option('-p',
                          dest='port',
                          type='int',
                          help='server port (default: %default)',
                          metavar='tcpPort',
                          default=8194)
        
        (options, args) = parser.parse_args()
        return options
    
    def process_message(self, msg):
        dic_output = dict()
        if not msg.hasElement(SECURITY_DATA):
            print('Unexpected message.')
            print(msg)
            return
        
        security_data_array = msg.getElement(SECURITY_DATA)
        
        if self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.PER_REQUEST:
            for security_data in security_data_array.values():
                security_name = security_data.getElementAsString(SECURITY)
                if not security_name in self.__dic_data:
                    self.__dic_data[security_data.getElementAsString(SECURITY)] = dict()
                
                field_data = security_data.getElement(FIELD_DATA)
                for field in field_data.elements():
                    if field.isValid():
                        field_name = str(field.name())
                        if field.isArray():
                            num_fields = field.numValues()
                            sub_fields = [field.getValueAsElement(x) for x in range(num_fields)]                            
                            if field_name in self.__dic_data[security_name]:
                                for sub_field in sub_fields:
                                    self.__dic_data[security_name][field_name][sub_field.getElement(0).getValueAsString()] = -99
                            else:
                                self.__dic_data[security_name][field_name] = {'|'.join([element.getValueAsString() for element in sub_field.elements()]):-99 for sub_field in sub_fields}
                        else:                            
                            self.__dic_data[security_name][field_name] = field.getValueAsString()
                    else:
                        print(field.name(), ' is NULL')
                        
                field_exception_array = security_data.getElement(FIELD_EXCEPTIONS)
                for field_exception in field_exception_array.values():
                    error_info = field_exception.getElement(ERROR_INFO)
                    print(error_info.getElementAsString('category'), ':', field_exception.getElementAsString(FIELD_ID))
                    
        elif self.__enum_data_request_type == ENUM_DATA_REQUEST_TYPES.HISTORICAL:
            security_name = security_data_array.getElementAsString(SECURITY)
            field_data = security_data_array.getElement(FIELD_DATA)
            num_sub_fields = field_data.numValues()
            sub_fields = [field_data.getValueAsElement(x) for x in range(num_sub_fields)]
            
            if not security_name in self.__dic_data:
                self.__dic_data[security_name] = dict()
                
            for sub_field in sub_fields:
                for field_req in self.__lst_fields:
                    if sub_field.hasElement(blpapi.Name(field_req)):
                        if not field_req in self.__dic_data[security_name]:
                            self.__dic_data[security_name][field_req] = {sub_field.getElementAsString(DATE):sub_field.getElementAsString(blpapi.Name(field_req))}
                        else:
                            self.__dic_data[security_name][field_req][sub_field.getElementAsString(DATE)] = sub_field.getElementAsString(blpapi.Name(field_req))
        return dic_output
    
if __name__ == '__main__':
    x = bloomberg_bdp('700 HK EQUITY', 'PX_LAST')
    x = bloomberg_bdp(['700 HK EQUITY', 'JD UQ EQUITY'], 'PX_LAST')
    x = bloomberg_bdp('700 HK EQUITY', ['PX_LAST','PX_BID','PX_ASK'])
    x = bloomberg_bdp(['700 HK EQUITY','JD UQ EQUITY'], ['PX_LAST','PX_BID','PX_ASK'])
    
    x = bloomberg_bds('700 HK EQUITY','OPT_CHAIN')
    x = bloomberg_bdh(['700 HK EQUITY', 'JD UQ EQUITY'], ['PX_LAST','PX_BID'], '20121221', '20181228')
    x = bloomberg_bds('USD CURNCY', 'CALENDAR_NON_SETTLEMENT_DATES', 'CALENDAR_START_DATE=20190101', 'CALENDAR_END_DATE=20191231')
    
    print(x)