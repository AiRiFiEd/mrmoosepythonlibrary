# -*- coding: utf-8 -*-
"""
Created on Wed Jan 30 22:42:06 2019

@author: LIM YUAN QING
"""

## Python Modules
import enum
import logging
import math
import scipy.stats
import pandas as pd

## Custom Modules
import modUtils3 as utils
#import modBloomberg3 as bbg

## Log Settings
str_format = '%(asctime)s:%(levelname)s:%(message)s'
formatter = logging.Formatter(str_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

## Module Enums
@enum.unique
class ENUM_OPTION_TYPE(enum.Enum):
    EUROPEAN_CALL = 1
    EUROPEAN_PUT = 2
    AMERICAN_CALL = 3
    AMERICAN_PUT = 4

@enum.unique
class ENUM_PRODUCT_TYPE(enum.Enum):
    VANILLA = 1
    ELSN = 2
    ELN = 3
    FCN = 4    

@enum.unique
class ENUM_ASSET_CLASS(enum.Enum):
    EQUITY = 1
    CURRENCY = 2
    INDEX = 3
    COMMODITY = 4    

@enum.unique
class ENUM_DERIVATIVE_METHOD(enum.Enum):
    CENTRAL = 1
    FORWARD = 2
    BACKWARD = 3

@enum.unique
class ENUM_FORWARD_ASSET_CLASS(enum.Enum):
    EQ = 1
    FX = 2
    IR = 3


class Portfolio(object):
    def __init__(self):
        pass
    
    def __repr__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
class Trade(object):
    def __init__(self, enum_product_type, dic_trade_param):
        pass
    
    def __repr__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass

class PricingModel(object):
    def __init__(self):
        pass
    
    # for del method
    def __del__(self):
        pass
    
    def __repr__(self):
        pass
    
    # for print()
    def __str__(self):
        pass
    
    # for len()
    def __len__(self):
        pass
    
    def price(self):
        pass
    
    def gen_greeks_basic(self):
        pass
    
    def gen_greeks_full(self):
        pass

class Underlying():
    def __init__(self, 
                 str_bloomberg_symbol):
        self.__str_bloomberg_symbol = str_bloomberg_symbol.upper()
        info = bbg.bloomberg_bdp(self.__str_bloomberg_symbol,
                                 ['BPIPE_REFERENCE_SECURITY_CLASS',
                                  'CRNCY',
                                  'DVD_CRNCY'])
        
        self.__str_asset_class = info[0][0]
        self.__str_currency = info[0][1]
        self.__str_dvd_currency = info[0][2]
        

        
    

class BlackScholesModel(PricingModel):
    
    int_option_count = 0
    def __init__(self,                
                 enum_option_type,
                 dbl_initial_price,
                 dbl_strike_price,
                 dbl_time_to_maturity,
                 dbl_riskfree_rate,
                 dbl_volatility,
                 dbl_dividend_yield):
        
        self.__enum_option_type = enum_option_type
        self.__dbl_initial_price = float(dbl_initial_price)
        self.__dbl_strike_price = float(dbl_strike_price)
        self.__dbl_time_to_maturity = float(dbl_time_to_maturity)
        self.__dbl_riskfree_rate = float(dbl_riskfree_rate)
        self.__dbl_volatility = float(dbl_volatility)
        self.__dbl_dividend_yield = float(dbl_dividend_yield)
                
        self.update_riskfree_discount()
        self.update_dividend_discount()        
        self.update_cost_of_carry()        
        
        BlackScholesModel.int_option_count += 1
    
    def __del__(self):
        BlackScholesModel.int_option_count -= 1
        
    def __repr__(self):
        return (self.__class__.__name__ + '(' +
                str(self.__enum_option_type) + ',"' +
                str(self.__dbl_initial_price) + '",' +
                str(self.__dbl_strike_price) + ',' +
                str(self.__dbl_time_to_maturity) + ',' +
                str(self.__dbl_riskfree_rate) + ',' +
                str(self.__dbl_volatility) + ',' +
                str(self.__dbl_dividend_yield) + ')')
    
    def __len__(self):
        pass
   
    def __str__(self):
        return '''
        Option #{int_option_count} \n
        
        Type: {enum_option_type} \n
        Spot: {dbl_initial_price} \n
        Strike: {dbl_strike_price} \n
        Time To Maturity: {dbl_time_to_maturity} \n
        Riskfree Rate: {dbl_riskfree_rate} \n
        Volatility: {dbl_volatility} \n
        Dividend Yield: {dbl_dividend_yield} \n    
        '''.format(int_option_count = BlackScholesModel.int_option_count,
                    enum_option_type = self.__enum_option_type,
                    dbl_initial_price = self.__dbl_initial_price,
                    dbl_strike_price = self.__dbl_strike_price,
                    dbl_time_to_maturity = self.__dbl_time_to_maturity,
                    dbl_riskfree_rate = self.__dbl_riskfree_rate,
                    dbl_volatility = self.__dbl_volatility,
                    dbl_dividend_yield = self.__dbl_dividend_yield)

    def update_cost_of_carry(self):
        self.__dbl_cost_of_carry = self.__dbl_riskfree_rate - self.__dbl_dividend_yield 
        self.update_d1()
        return self.__dbl_cost_of_carry

    def update_d1(self):
        self.__dbl_d1 = (
                (math.log(self.__dbl_initial_price/self.__dbl_strike_price) +
                 (self.__dbl_cost_of_carry + (self.__dbl_volatility**2.0)/2.0) * self.__dbl_time_to_maturity) /
                 (self.__dbl_volatility * (self.__dbl_time_to_maturity ** 0.5))  
                 )
        self.update_d2()
        return self.__dbl_d1        
                
    def update_d2(self):
        self.__dbl_d2 = self.__dbl_d1 - (self.__dbl_volatility * (self.__dbl_time_to_maturity ** 0.5))
        self.update_densities()
        self.price()
        return self.__dbl_d2
    
    def update_densities(self):
        self.__dbl_pdf_d1 = scipy.stats.norm.pdf(self.__dbl_d1)
        self.__dbl_pdf_d2 = scipy.stats.norm.pdf(self.__dbl_d2)
        self.__dbl_cdf_d1 = scipy.stats.norm.cdf(self.__dbl_d1,0.0,1.0)
        self.__dbl_cdf_d2 = scipy.stats.norm.cdf(self.__dbl_d2,0.0,1.0)
        return (self.__dbl_pdf_d1, self.__dbl_cdf_d1, self.__dbl_pdf_d2, self.__dbl_cdf_d2)        
    
    def update_dividend_discount(self):
        self.__dbl_dividend_discount = math.exp(- self.__dbl_dividend_yield *self.__dbl_time_to_maturity)
        return self.__dbl_dividend_discount
    
    def update_riskfree_discount(self):
        self.__dbl_riskfree_discount = math.exp(-self.__dbl_riskfree_rate * self.__dbl_time_to_maturity)
        return self.__dbl_riskfree_discount

    def price(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            self.__dbl_price = ((self.__dbl_strike_price * 
                                 self.__dbl_riskfree_discount *
                                 (1.0-self.__dbl_cdf_d2)) -
                                (self.__dbl_initial_price * 
                                 self.__dbl_dividend_discount *
                                 (1.0-self.__dbl_cdf_d1)))
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            self.__dbl_price = ((self.__dbl_initial_price * 
                                 self.__dbl_dividend_discount *
                                 self.__dbl_cdf_d1) -
                                (self.__dbl_strike_price * 
                                 self.__dbl_riskfree_discount *
                                 self.__dbl_cdf_d2))
        return self.__dbl_price
    
    def gen_greeks_basic(self):
        self.__dic_greeks = dict()
        self.__dic_greeks['SPOT_DELTA'] = self.gen_spot_delta()
        self.__dic_
        return self.__dic_greeks

    def gen_greeks_full(self):
        self.__dic_greeks = dict()
        self.__dic_greeks['SPOT_DELTA'] = self.gen_spot_delta()
        self.__dic_greeks['VANNA'] = self.gen_vanna()
        self.__dic_greeks['CHARM'] = self.gen_charm()
        self.__dic_greeks['GAMMA'] = self.gen_gamma()
        self.__dic_greeks['GAMMA_PERC'] = self.gen_gamma_perc()
        self.__dic_greeks['ZOMMA'] = self.gen_zomma()
        self.__dic_greeks['ZOMMA_PERC'] = self.gen_zomma_perc()
        self.__dic_greeks['SPEED'] = self.gen_speed()
        self.__dic_greeks['SPEED_PERC'] = self.gen_speed_perc()
        self.__dic_greeks['COLOUR'] = self.gen_colour()
        self.__dic_greeks['COLOUR_PERC'] = self.gen_colour_perc()
        self.__dic_greeks['VEGA'] = self.gen_vega()        
        self.__dic_greeks['VEGA_PERC'] = self.gen_vega()        
        self.__dic_greeks['VOMMA'] = self.gen_vomma()
        self.__dic_greeks['VOMMA_PERC'] = self.gen_vomma_perc()
        self.__dic_greeks['ULTIMA'] = self.gen_ultima()
        self.__dic_greeks['VEGA_BLEED'] = self.gen_vega_bleed()
        self.__dic_greeks['THETA'] = self.gen_theta()
        self.__dic_greeks['THETA_THEORETICAL'] = self.gen_theta(True)
        self.__dic_greeks['RHO'] = self.gen_rho()
        return self.__dic_greeks

    def gen_spot_delta(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            return (self.__dbl_dividend_discount*(self.__dbl_cdf_d1 - 1.0))            
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            return (self.__dbl_dividend_discount*self.__dbl_cdf_d1)

    def gen_vanna(self, variance_form = False):
        vanna = ((-self.__dbl_dividend_discount * self.__dbl_d2 * self.__dbl_pdf_d1)/
                self.__dbl_volatility)
        if variance_form:
            return vanna * (self.__dbl_initial_price/(2.0*self.__dbl_volatility))
        else:
            return vanna
           
    def gen_charm(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            return (-self.__dbl_dividend_discount * ( 
                    (self.__dbl_pdf_d1 * ((self.__dbl_cost_of_carry/
                        (self.__dbl_volatility * self.__dbl_time_to_maturity**0.5))-
                        (self.__dbl_d2 / (2.0*self.__dbl_time_to_maturity)))) -
                    ((self.__dbl_cost_of_carry-self.__dbl_riskfree_rate)*(1.0-self.__dbl_cdf_d1))
                        )
                    )
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            return (-self.__dbl_dividend_discount * ( 
                    (self.__dbl_pdf_d1 * ((self.__dbl_cost_of_carry/
                        (self.__dbl_volatility * self.__dbl_time_to_maturity**0.5))-
                        (self.__dbl_d2 / (2.0*self.__dbl_time_to_maturity)))) +
                    ((self.__dbl_cost_of_carry-self.__dbl_riskfree_rate)*(self.__dbl_cdf_d1))
                        )
                    )

    def gen_gamma(self):
        return ((self.__dbl_pdf_d1 * self.__dbl_dividend_discount) /
                 (self.__dbl_initial_price * self.__dbl_volatility * 
                  (self.__dbl_time_to_maturity**0.5)))
    
    def gen_gamma_perc(self):
        return (self.gen_gamma() * self.__dbl_initial_price) / 100.0
    
    def gen_zomma(self):
        return self.gen_gamma() * ((self.__dbl_d1 * self.__dbl_d2 - 1.0)/self.__dbl_volatility)
    
    def gen_zomma_perc(self):
        return self.gen_gamma_perc() * ((self.__dbl_d1 * self.__dbl_d2 - 1.0)/self.__dbl_volatility)
    
    # d(gamma)/d(spot)
    def gen_speed(self):
        return (-self.gen_gamma()*(1.0 + (self.__dbl_d1/(self.__dbl_volatility * self.__dbl_time_to_maturity**0.5))))/self.__dbl_initial_price
    
    def gen_speed_perc(self):
        return (-self.gen_gamma()*self.__dbl_d1) / (100.0 * self.__dbl_volatility * self.__dbl_time_to_maturity**0.5)
    
    def gen_colour(self):
        return (self.gen_gamma() * (self.__dbl_riskfree_rate - self.__dbl_cost_of_carry + 
                              ((self.__dbl_cost_of_carry * self.__dbl_d1)/(self.__dbl_volatility*self.__dbl_time_to_maturity**0.5)) + 
                              ((1.0 - self.__dbl_d1 * self.__dbl_d2)/(2.0*self.__dbl_time_to_maturity))))
                
    def gen_colour_perc(self):
        return (self.gen_gamma_perc() * (self.__dbl_riskfree_rate - self.__dbl_cost_of_carry + 
                              ((self.__dbl_cost_of_carry * self.__dbl_d1)/(self.__dbl_volatility*self.__dbl_time_to_maturity**0.5)) + 
                              ((1.0 - self.__dbl_d1 * self.__dbl_d2)/(2.0*self.__dbl_time_to_maturity))))
    
    def gen_vega(self, variance_form = False):
        vega = (self.__dbl_initial_price * self.__dbl_dividend_discount *
                self.__dbl_pdf_d1 * (self.__dbl_time_to_maturity ** 0.5))
        if variance_form:
            return vega / (2.0*self.__dbl_volatility)
        else:
            return vega
        
    def gen_vega_perc(self):
        return (self.__dbl_volatility/10.0) * self.gen_vega()
    
    def gen_vomma(self, variance_form = False):
        if variance_form:
            return ((self.gen_vega(True) / (2.0 * self.__dbl_volatility**2.0)) * 
                    (self.__dbl_d1*self.__dbl_d2 - 1.0))
        else:
            return self.gen_vega() * ((self.__dbl_d1*self.__dbl_d2)/self.__dbl_volatility) 
    
    def gen_vomma_perc(self):
        return self.gen_vega_perc() * ((self.__dbl_d1*self.__dbl_d2)/self.__dbl_volatility)
    
    def gen_ultima(self):
        return (self.gen_vomma() * (1.0/self.__dbl_volatility) * 
                (self.__dbl_d1 * self.__dbl_d2 - 
                 self.__dbl_d1 / self.__dbl_d2 - 
                 self.__dbl_d2 / self.__dbl_d1 - 1.0)
                )
                
    def gen_vega_bleed(self):
        return self.gen_vega() * (self.__dbl_riskfree_rate - self.__dbl_cost_of_carry +
                            ((self.__dbl_cost_of_carry * self.__dbl_d1) / (self.__dbl_volatility * self.__dbl_time_to_maturity**0.5)) - 
                            ((1.0 + self.__dbl_d1 * self.__dbl_d2) / (2.0 * self.__dbl_time_to_maturity)))
    
    def gen_theta(self, bln_theoratical = False):
        if bln_theoratical:
            if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
                return (
                        ((-self.__dbl_initial_price * self.__dbl_dividend_discount * self.__dbl_pdf_d1 * self.__dbl_volatility)/(2.0*self.__dbl_time_to_maturity**0.5)) +        
                            ((self.__dbl_cost_of_carry-self.__dbl_riskfree_rate) * self.__dbl_initial_price * self.__dbl_dividend_discount * (1.0 - self.__dbl_cdf_d1)) + 
                            ((self.__dbl_riskfree_rate*self.__dbl_strike_price*self.__dbl_riskfree_discount*(1.0-self.__dbl_cdf_d2)))
                            )        
            elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
                return (
                        ((-self.__dbl_initial_price * self.__dbl_dividend_discount * self.__dbl_pdf_d1 * self.__dbl_volatility)/(2.0*self.__dbl_time_to_maturity**0.5)) -     
                            ((self.__dbl_cost_of_carry-self.__dbl_riskfree_rate) * self.__dbl_initial_price * self.__dbl_dividend_discount * self.__dbl_cdf_d1) -
                            ((self.__dbl_riskfree_rate*self.__dbl_strike_price*self.__dbl_riskfree_discount*self.__dbl_cdf_d2))
                            )
        else:
            dbl_time_to_maturity_old = self.get_time_to_maturity()
            dbl_price_old = self.price()
            self.set_time_to_maturity(dbl_time_to_maturity_old - 1.0/360.0)
            theta = self.price() - dbl_price_old
            self.set_time_to_maturity(dbl_time_to_maturity_old)
            self.price()
            return theta
        
    def gen_rho(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            return (-self.__dbl_time_to_maturity * self.__dbl_strike_price * 
                    math.exp(-self.__dbl_riskfree_rate*self.__dbl_time_to_maturity) * 
                    (1.0-self.__dbl_cdf_d2))
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            return (self.__dbl_time_to_maturity * self.__dbl_strike_price * 
                    math.exp(-self.__dbl_riskfree_rate*self.__dbl_time_to_maturity) * 
                    self.__dbl_cdf_d2)
    ## Getters

    def get_initial_price(self):
        return self.__dbl_initial_price
    
    def get_strike_price(self):
        return self.__dbl_strike_price
    
    def get_time_to_maturity(self):
        return self.__dbl_time_to_maturity
    
    def get_riskfree_rate(self):
        return self.__dbl_riskfree_rate
    
    def get_volatility(self):
        return self.__dbl_volatility
    
    def get_dividend_yield(self):
        return self.__dbl_dividend_yield
    
    
    ## Setters
    
    def set_initial_price(self, dbl_initial_price):
        self.__dbl_initial_price = dbl_initial_price
        self.update_d1()        
        return self.__dbl_initial_price
    
    def set_strike_price(self, dbl_strike_price):
        self.__dbl_strike_price = dbl_strike_price
        self.update_d1()        
        return self.__dbl_strike_price
    
    def set_time_to_maturity(self, dbl_time_to_maturity):
        self.__dbl_time_to_maturity = dbl_time_to_maturity
        self.update_d1()        
        return self.__dbl_time_to_maturity
    
    def set_riskfree_rate(self, dbl_riskfree_rate):
        self.__dbl_riskfree_rate = dbl_riskfree_rate
        self.update_riskfree_discount()
        self.update_cost_of_carry()
        return self.__dbl_riskfree_rate
    
    def set_volatility(self, dbl_volatility):
        self.__dbl_volatility = dbl_volatility
        self.update_d1()        
        return self.__dbl_volatility
    
    def set_dividend_yield(self, dbl_dividend_yield):
        self.__dbl_dividend_yield = dbl_dividend_yield
        self.update_dividend_discount()
        self.update_cost_of_carry()
        return self.__dbl_dividend_yield
    
    

def discounted_dividend(start_date, end_date, div_dates, div_amount):
    pass

def div_yield(lst_schedule):
    pass

class RiskFreeCurve:
    def __init__(self):
        pass
    
    def __del__(self):
        pass
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
class MarketConventions:
    def __init__(self, str_market):
        self.__str_market = str_market
        try:
            self.__str_currency = self.gen_currency()
        except KeyError:
            print('Unsupported market.')
            return
    
    def __del__(self):
        print('Object deleted.')
    
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def gen_currency(self):
        return {'UN':'USD',
                    'UQ':'USD',
                    'UW':'USD',
                    'US':'USD',
                    'UP':'USD',
                    'EU':'EUR',
                    'GY':'EUR',
                    'FP':'EUR',
                    'LN':'GBP',
                    'NA':'EUR',
                    'SW':'CHF',
                    'SG':'SGD',
                    'SP':'SGD',
                    'HK':'HKD',
                    'AU':'AUD',
                    'AT':'AUD',
                    'JP':'JPY',
                    'JT':'JPY',
                    'MA':'MYR',
                    'MK':'MYR',
                    'TH':'THB',
                    'TB':'THB'}[self.__str_market]
        
    def gen_calendar_code(self):
        return {'USD':'US',
                'SGD':'SI',
                'MYR':'MA',
                'AUD':'AU',
                'HKD':'HK',
                'JPY':'JN',
                'EUR':'USD'}
        
def forward(initial, risk_free, time_to_maturity, 
                asset_class = ENUM_FORWARD_ASSET_CLASS.EQ):
    """
    Compute the forward rate
    
    Parameters
    ----------
    initial : double
        initial spot value
    risk_free : double
        risk-free rate
    time_to_maturity : double
        time to maturity
    asset_class : ENUM_FORWARD_ASSET_CLASS
        enum to indicate asset class: EQ, FX, IR
        
    Returns
    -------
    float
        forward rate
        
    Raises
    ------
    ValueError
        when an invalid method enum is passed to function
        
    Source(s)
    ---------
    [1] Bloomberg
    """
    if asset_class == ENUM_FORWARD_ASSET_CLASS.EQ:
        pass
    elif asset_class == ENUM_FORWARD_ASSET_CLASS.FX:
        pass
    elif asset_class == ENUM_FORWARD_ASSET_CLASS.IR:
        pass
    else:
        raise ValueError('''asset_class must be ENUM_FORWARD_ASSET_CLASS.EQ, )
                                ENUM_FORWARD_ASSET_CLASS.FX,
                                ENUM_FORWARD_ASSET_CLASS.IR''')        
        
def differentiate(f, x, step=0.01, method=ENUM_DERIVATIVE_METHOD.CENTRAL):
    """
    Compute the derivative of f
    
    Parameters
    ----------
    f : object
        function of one variable
    x : double
        point at which to compute derivative
    step : double
        step size in difference formula
    method : ENUM_DERIVATIVE_METHOD
        enum to determine difference formula: CENTRAL, FORWARD, BACKWARD
        
    Returns
    -------
    float
        Difference formula:
            ENUM_DERIVATIVE_METHOD.CENTRAL:  [f(x+step)-f(x-step)]/(2*step)
            ENUM_DERIVATIVE_METHOD.FORWARD:  [f(x+step)-f(x)]/(step)
            ENUM_DERIVATIVE_METHOD.BACKWARD: [f(x)-f(x-step)]/(step)
            
    Raises
    ------
    ValueError
        when an invalid method enum is passed to function
        
    Source(s)
    ---------
    [1] http://www.math.ubc.ca/~pwalls/math-python/differentiation/    
    """
    
    if method == ENUM_DERIVATIVE_METHOD.CENTRAL:
        return (f(x+step)-f(x-step))/(2*step)
    elif method == ENUM_DERIVATIVE_METHOD.FORWARD:
        return (f(x+step)-f(x))/(step)
    elif method == ENUM_DERIVATIVE_METHOD.BACKWARD:
        return (f(x)-f(x-step))/(step)
    else:
        raise ValueError('''method must be ENUM_DERIVATIVE_METHOD.CENTRAL, 
                                 ENUM_DERIVATIVE_METHOD.FORWARD, 
                                 ENUM_DERIVATIVE_METHOD.BACKWARD''')
    
def partial_derivative():
    pass

if __name__ == '__main__':
    #underlying = Underlying('700 HK EQUITY')
    bsm = BlackScholesModel(ENUM_OPTION_TYPE.EUROPEAN_CALL,
                            382.10,
                            380.,
                            90.0/360.0,
                            0.02060,
                            0.27801,
                           0.01064)
    
    print(bsm.gen_greeks_full())
#    bsm2 = eval(bsm.__repr__())
#    print(bsm2)
    
    
    