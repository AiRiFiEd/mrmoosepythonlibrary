# -*- coding: utf-8 -*-
"""
Created on Sat Oct 22 09:03:53 2016

@author: Lim Yuan Qing
"""
# Python modules
from math import log
from math import exp
import scipy
import pandas as pd
import enum
import logging

# Custom modules
import modUtils3 as utils

str_format = '%(asctime)s:%(levelname)s:%(message)s'
formatter = logging.Formatter(str_format)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(__name__ + '.log')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

@enum.unique
class ENUM_OPTION_TYPE(enum.Enum):
    EUROPEAN_CALL = 1
    EUROPEAN_PUT = 2
    AMERICAN_CALL = 3
    AMERICAN_PUT = 4



        
    



class BlackScholesModel_OLD():

    __int_option_count = 0
    def __init__(self, enum_option_type, 
                 dbl_initial_price, 
                 dbl_strike_price, 
                 dbl_time_to_maturity,
                 dbl_riskfree_rate,
                 dbl_volatility,
                 dbl_dividend_yield):
        
        self.__enum_option_type = enum_option_type
        self.__dbl_initial_price = dbl_initial_price
        self.__dbl_strike_price = dbl_strike_price
        self.__dbl_time_to_maturity = dbl_time_to_maturity
        self.__dbl_riskfree_rate = dbl_riskfree_rate
        self.__dbl_volatility = dbl_volatility
        self.__dbl_dividend_yield = dbl_dividend_yield
        self.__dbl_cost_of_carry = self.__dbl_riskfree_rate - self.__dbl_dividend_yield
        self.gen_d1()
        self.gen_d2()
        BlackScholesModel.__int_option_count += 1
                
    def __del__(self):
        BlackScholesModel.__int_option_count -= 1
        
    def __str__(self):
        pass
    
    def __len__(self):
        pass
    
    def gen_d1(self):
        self.__dbl_d1 = (
                        (log(self.__dbl_initial_price/self.__dbl_strike_price) +
                         (self.__dbl_cost_of_carry + (self.__dbl_volatility**2)/2) * self.__dbl_time_to_maturity) /
                         (self.__dbl_volatility * (self.__dbl_time_to_maturity ** 0.5))                
                        )
        return self.__dbl_d1
                
    def gen_d2(self):
        self.__dbl_d2 = self.__dbl_d1 - (self.__dbl_volatility * (self.__dbl_time_to_maturity ** 0.5))
        return self.__dbl_d2
        
    def gen_price(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            self.__dbl_price = ((self.__dbl_strike_price * 
                                 exp(-self.__dbl_riskfree_rate * self.__dbl_time_to_maturity) *
                                 scipy.stats.norm.cdf(-self.__dbl_d2,0.0,1.0)) -
                                (self.__dbl_initial_price * 
                                 exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate) * self.__dbl_time_to_maturity) *
                                 scipy.stats.norm.cdf(-self.__dbl_d1,0.0,1.0)))
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            self.__dbl_price = ((self.__dbl_initial_price * 
                                 exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate) * self.__dbl_time_to_maturity) *
                                 scipy.stats.norm.cdf(self.__dbl_d1,0.0,1.0)) -
                                (self.__dbl_strike_price * 
                                 exp(-self.__dbl_riskfree_rate * self.__dbl_time_to_maturity) *
                                 scipy.stats.norm.cdf(self.__dbl_d2,0.0,1.0)))
        return self.__dbl_price

    def gen_parity_price(self):
        self.gen_price()
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            self.__dbl_parity_price = (self.__dbl_price  + 
                                       self.__dbl_initial_price * exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate)* self.__dbl_time_to_maturity) - 
                                       self.__dbl_strike_price * exp(-self.__dbl_riskfree_rate * self.__dbl_time_to_maturity))
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            self.__dbl_parity_price = (self.__dbl_price  - 
                                       self.__dbl_initial_price * exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate) * self.__dbl_time_to_maturity) + 
                                       self.__dbl_strike_price * exp(-self.__dbl_riskfree_rate * self.__dbl_time_to_maturity))            
        return self.__dbl_parity_price

    def gen_cost_of_carry(self):
        self.__dbl_cost_of_carry = self.__dbl_riskfree_rate - self.__dbl_dividend_yield
        return self.__dbl_cost_of_carry
    
    def gen_delta(self):
        if self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_PUT:
            self.__dbl_delta = (exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate)
                                    *self.__dbl_time_to_maturity) * 
                                (scipy.stats.norm.cdf(self.__dbl_d1,0.0,1.0)-1))
        elif self.__enum_option_type == ENUM_OPTION_TYPE.EUROPEAN_CALL:
            self.__dbl_delta = (exp((self.__dbl_cost_of_carry - self.__dbl_riskfree_rate)
                                    *self.__dbl_time_to_maturity) * 
                                scipy.stats.norm.cdf(self.__dbl_d1,0.0,1.0))
        return self.__dbl_delta
    
    def gen_gamma(self):
        pass
    
    def get_option_type(self):
        return self.__enum_option_type
        
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
    
    def get_cost_of_carry(self):
        return self.__dbl_cost_of_carry
    
    def get_price(self):
        self.gen_price()
        return self.__dbl_price
    
    def get_parity_price(self):
        self.gen_parity_price()
        return self.__dbl_parity_price
    
    def set_option_type(self, enum_option_type):
        self.__enum_option_type = enum_option_type
    
    def set_initial_price(self, dbl_initial_price):
        self.__dbl_initial_price = dbl_initial_price
        
    def set_strike_price(self, dbl_strike_price):
        self.__dbl_strike_price = dbl_strike_price
        
    def set_time_to_maturity(self, dbl_time_to_maturity):
        self.__dbl_time_to_maturity = dbl_time_to_maturity
        
    def set_riskfree_rate(self, dbl_riskfree_rate):
        self.__dbl_riskfree_rate = dbl_riskfree_rate
        self.gen_cost_of_carry()
        
    def set_volatility(self, dbl_volatility):
        self.__dbl_volatility = dbl_volatility
        
    def set_dividend_yield(self, dbl_dividend_yield):
        self.__dbl_dividend_yield = dbl_dividend_yield   
        self.gen_cost_of_carry()
        
    
        
    
    
    
    
    
    
    
    
    
# =============================================================================
#     
#     (math.log(self.__dblDiscountedInitialPrice / self.__dblStrike) + (self.__dblRiskFreeRate - self.__dblDividendYield + 0.5 * self.__dblVolatility ** 2) * self.__dblTimeToMaturity) / (self.__dblVolatility * math.sqrt(self.__dblTimeToMaturity))
#     
#     
#     def getCallPrice(self):
#         self.__dblDiscountedInitialPrice = self.__dblInitialPrice * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity)
#         self.__dbld1 = (math.log(self.__dblDiscountedInitialPrice / self.__dblStrike) + (self.__dblRiskFreeRate - self.__dblDividendYield + 0.5 * self.__dblVolatility ** 2) * self.__dblTimeToMaturity) / (self.__dblVolatility * math.sqrt(self.__dblTimeToMaturity))
#         self.__dbld2 = (math.log(self.__dblDiscountedInitialPrice / self.__dblStrike) + (self.__dblRiskFreeRate - self.__dblDividendYield - 0.5 * self.__dblVolatility ** 2) * self.__dblTimeToMaturity) / (self.__dblVolatility * math.sqrt(self.__dblTimeToMaturity))
#         return (self.__dblDiscountedInitialPrice * scipy.stats.norm.cdf(self.__dbld1,0.0,1.0) - self.__dblStrike * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(self.__dbld2,0.0,1.0))
#     def getPutPrice(self):
#         return self.getCallPrice() + self.__dblStrike * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) - self.__dblInitialPrice
#     def getCallDelta(self):
#         return math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(self.__dbld1,0.0,1.0)
#     def getPutDelta(self):
#         return math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) * (scipy.stats.norm.cdf(self.__dbld1,0.0,1.0)-1.0)
#     def getGamma(self):
#         return (scipy.stats.norm.pdf(self.__dbld1) * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity)) / (self.__dblInitialPrice * self.__dblVolatility * math.sqrt(self.__dblTimeToMaturity))
#     def getVega(self):
#         return self.__dblInitialPrice * scipy.stats.norm.pdf(self.__dbld1) * math.sqrt(self.__dblTimeToMaturity) * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity)
#     def getCallTheta(self):
#         return ((-self.__dblInitialPrice * scipy.stats.norm.pdf(self.__dbld1) * self.__dblVolatility * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) / (2 * math.sqrt(self.__dblTimeToMaturity))) + 
#                 (self.__dblDividendYield * self.__dblInitialPrice * scipy.stats.norm.pdf(self.__dbld1) * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) -
#                  self.__dblRiskFreeRate * self.__dblStrike * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(self.__dbld2,0.0,1.0)))
#     def getPutTheta(self):
#         return ((-self.__dblInitialPrice * scipy.stats.norm.pdf(self.__dbld1) * self.__dblVolatility * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) / (2 * math.sqrt(self.__dblTimeToMaturity))) - 
#                 (self.__dblDividendYield * self.__dblInitialPrice * scipy.stats.norm.pdf(self.__dbld1) * math.exp(-self.__dblDividendYield * self.__dblTimeToMaturity) +
#                  self.__dblRiskFreeRate * self.__dblStrike * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(self.__dbld2,0.0,1.0)))
#     def getCallRho(self):
#         return self.__dblStrike * self.__dblTimeToMaturity * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(self.__dbld2,0.0,1.0)
#     def getPutRho(self):
#         return -self.__dblStrike * self.__dblTimeToMaturity * math.exp(-self.__dblRiskFreeRate * self.__dblTimeToMaturity) * scipy.stats.norm.cdf(-self.__dbld2,0.0,1.0)
#     def displayOptionDetails(self):
#         df = pd.DataFrame(
#                           [[self.getCallPrice(), self.getPutPrice()],
#                           [self.getCallDelta(), self.getPutDelta()],
#                           [self.getGamma(), self.getGamma()],
#                           [self.getVega(), self.getVega()],
#                           [self.getCallTheta(), self.getPutTheta()],
#                           [self.getCallRho(), self.getPutRho()]],
#                           columns = ['Call', 'Put'],
#                           index = ['Price', 'Delta', 'Gamma', 'Vega', 'Theta', 'Rho']
#                           )
#         print(df)
# =============================================================================

if __name__ == '__main__':
    DBS = BlackScholesModel(ENUM_OPTION_TYPE.EUROPEAN_PUT,49.0,50.0,2.0,0.05,0.20,0.0)
# =============================================================================
#     print(DBS.getCallPrice())
#     print(DBS.getPutPrice())
#     print(DBS.getCallDelta())
#     print(DBS.getPutDelta())
#     print(DBS.getGamma())
#     print(DBS.getCallTheta())
#     print(DBS.getPutTheta())
#     print(DBS.getCallRho())
#     print(DBS.getPutRho())
#     DBS.displayOptionDetails()
#     del DBS
# =============================================================================
    #fnc_outlook_email(6)