import numpy as np
from datetime import datetime

class Ad:

    def __init__(
        self,
        accountId,
        adId,
        impression,
        click,
        budgetSpent,
        budgetTotal,
        startDate,
        endDate
    ):
        self.__formatString = "%Y-%m-%d %H:%M:%S"

        assert isinstance(accountId, str), "Type Error. accountId must must be a string"
        self.__accountId   = accountId

        assert isinstance(adId, str), "Type Error. adId must must be a string"
        self.__adId        = adId

        assert impression >= 0, "Value Error. Impressions number cannot be less than 0"
        self.__impression = impression

        assert impression >= 0, "Value Error. Clicks number cannot be less than 0"
        self.__click       = click

        match budgetTotal >= budgetSpent:
            case True:
                self.__budgetSpent = budgetSpent
                self.__budgetTotal = budgetTotal
            case _:
                raise ValueError("Total budget cannot be less than spen budget")

        self.__budgetRemain = self.__budgetTotal - self.__budgetSpent

        self.__startDate, self.__endDate = self.__schedule(startDate, endDate)
        
        self.__valuePerClick = 1.15   

        match self.__impression == 0:
            case True:
                self.__cpm = 0
                self.__ctr = 0
            case _:  
                self.__cpm = (self.__budgetSpent / self.__impression) * 1000
                self.__ctr = self.__click / self.__impression

        match self.__click == 0:
            case True:
                self.__cpc = 0
            case _:
                self.__cpc = self.__budgetSpent / self.__click

        self.__point      = None
        self.__touchDate  = None
        self.__valuePerClick = 1.15

    def updateValuePerClick(self, x):

        assert x > 0, "Invalid value. Value per click cannot be less or equal zero."
        self.__valuePerClick = x
        
    @property
    def valuePerClick(self):
        return self.__valuePerClick

    def __schedule(self, startDate, endDate):
        
        startDate = datetime.strptime(startDate, self.__formatString)
        endDate   = datetime.strptime(endDate  , self.__formatString)

        match (endDate > startDate):
            case True:
                return (startDate, endDate)
            case _:
                raise ValueError(f"Invalid value. {endDate} cannot be less or equals to {startDate}")

    @property
    def formatString(self):
        return self.__formatString

    @property
    def meta(self):
        return {
            "accountId"   : self.__accountId,
            "adId"        : self.__adId,
            "impression"  : self.__impression,
            "click"       : self.__click,
            "ctr"         : self.__ctr,
            "budgetSpent" : self.__budgetSpent,
            "budgetRemain": self.__budgetRemain,
            "budgetTotal" : self.__budgetTotal,
            "valuePerClick": self.__valuePerClick,
            "cpm"         : self.__cpm,
            "cpc"         : self.__cpc,
            "startDate"   : self.__startDate,
            "endDate"     : self.__endDate,
            "touchDate"   : self.__touchDate
        }
    @property
    def point(self):

        return self.__point

    
    def __updateState(self, impression, click, cpm):

        self.__impression    += impression
        self.__click         += click
        self.__ctr           = self.__click / self.__impression
        self.__budgetSpent   += (cpm * impression) / 1000
        self.__cpm           = (self.__budgetSpent / self.__impression) * 1000
        self.__cpc           = self.__budgetSpent / self.__click
        self.__budgetRemain  = self.__budgetTotal - self.__budgetSpent
        self.__valuePerClick = self.__cpm / (1000 * self.__ctr)


    def update(self, point):

        match (self.__accountId == point.accountId) & (self.__adId == point.adId):
            case True:
                pass
            case _:
                raise ValueError("Incorrect accountId or adId")

        match (self.__startDate <= point.touchDate <= self.__endDate):
            case True:
                pass
            case _:
                raise ValueError("Incorrect value. Touch date cannot be less than start date or bigger than end date")


        self.__updateState(point.impression, point.click, point.cpm)
        self.__touchDate  = point.touchDate
        self.__point      = point.meta
