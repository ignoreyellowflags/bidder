import numpy as np
from datetime import datetime
from typing import Optional

class TelegramAd:

    def __init__(
        self,
        accountId  : str,
        adId       : str,
        dateStart  : str,
        dateEnd    : str
    ):
        self.__formatString = "%Y-%m-%d %H:%M:%S"

        assert isinstance(accountId, str), "Type Error. `accountId` must must be a string"
        self.__accountId   = accountId
        
        assert isinstance(adId, str)     , "Type Error. `adId` must must be a string"
        self.__adId        = adId

        self.__dateStart = self.convertStrToDate(dateStart)
        self.__dateEnd   = self.convertStrToDate(dateEnd)

        match (self.__dateEnd >= self.__dateStart):
            case True:
                pass
            case _:
                raise ValueError(f"Invalid value. {self.__dateEnd} cannot be less than {self.__dateStart}")

    @property
    def accountId(self) -> str:
        return self.__accountId
    @property
    def adId(self)      -> str:
        return self.__adId
    @property
    def dateEnd(self)   -> datetime:
        return self.__dateEnd
    @property
    def dateStart(self) -> datetime:
        return self.__dateStart

    def __hash__(self):
        return hash((self.__accountId, self.__adId))

    def __eq__(self, other):
        if not isinstance(other, TelegramAd):
            return NotImplemented  #!
        else:
            return self.__hash__() == other.__hash__()
            
    def __ne__(self, other):
        if not isinstance(other, TelegramAd):
            return NotImplemented
        else:
            return not self.__eq__(other)  

    def convertStrToDate(self, date: str) -> datetime:

        return datetime.strptime(date, self.__formatString)

    def extend(self, date: str) -> None:

        date        = self.convertStrToDate(date)
        match (date >= self.__dateEnd):
            case True:
                self.__dateEnd = date
            case _ :
                raise ValueError(f"Invalid value. Extended date cannot be less than {self.__dateEnd}")


class Ad(TelegramAd):

    def __init__(
        self                 ,
        accountId  : str     ,
        adId       : str     ,
        impression : int     ,
        click      : int     ,
        expenditure: float   ,
        dateStart  : str     ,
        dateEnd    : str     ,
        touchDate  : Optional[str]
    ):
        '''
        `accountID`   - | Unique identifier assigned user's account
        `adId`        - | Unique identifier assigned user's advertisment
        `impession`   - | Total number of impressions
        `click`       - | Total number of clicks
        `expenditure` - | Advertisment expenses (€)
        `dateStart`   - | Launch date
        `dateEnd`     - | Termination date
        `touchDate`   - | Actual date reflecting on current statistics
        '''
        
        super().__init__(
            accountId = accountId,
            adId      = adId,
            dateStart = dateStart,
            dateEnd   = dateEnd
        )

        assert impression    >= 0           , "Value Error. `impression` value cannot be less than 0"
        self.__impression    = int(impression)

        assert click         >= 0           , "Value Error. `click` value cannot be less than 0"
        self.__click         = int(click)

        assert expenditure   >= 0           , "Value Error. `expenditure` value cannot be less than 0"
        self.__expenditure   = float(expenditure)
        
        # touchDAte in middle check!!!!!
        
        self.__touchDate     = self.dateStart if touchDate == None else self.convertStrToDate(touchDate)

        match ( (self.__touchDate >= self.dateStart) and (self.__touchDate <= self.dateEnd) ):
            case True:
                pass
            case _:
                raise ValueError(f"{self.__touchDate} is out of boundaries")
        
        if self.__touchDate == self.dateStart:
            match ( (self.__impression > 0) or (self.__click > 0) or (self.__expenditure > 0) ):
                case True:
                    raise ValueError("`Ad` hasn't been launched so it's impossible to have statisticks like impression/click/expenditure")
                case _:
                    pass
        
        self.__cpm           = 0 if self.__impression == 0 else (self.__expenditure / self.__impression) * 1000
        self.__ctr           = 0 if self.__impression == 0 else self.__click / self.__impression
        self.__valuePerClick = 1.15 if self.__impression == 0 else self.__cpm / (1000 * self.__ctr)

    @property
    def impression(self):
        return self.__impression
    @property
    def click(self):
        return self.__click
    @property
    def expenditure(self):
        return self.__expenditure
    @property
    def valuePerClick(self):
        return self.__valuePerClick
    @property
    def touchDate(self):
        return self.__touchDate
    @property
    def cpm(self):
        return self.__cpm
    @property
    def ctr(self):
        return self.__ctr
        

    def update(self, impression: int, click: int, expenditure: float, touchDate: str) -> None:

        ''''
        Update `Ad` state according to new incoming statistics 

        `impession`   - | Total number of impressions (cummulative not incremental)
        `click`       - | Total number of clicks      (cummulative not incremental)
        `expenditure` - | Advertisment expenses (€)   (cummulative not incremental)
        '''

        assert click               >= 0, "Value Error. `click` value cannot be less than 0"
        assert expenditure         >  0, "Value Error. Cannot update `Ad` state having 0 `expenditure`"
        assert impression          >  0, "Value Error. Cannot update state of `Ad` having 0 `impression`"
        
        touchDate                  = self.convertStrToDate(touchDate)
        match (touchDate <= self.__touchDate):
            case True:
                raise ValueError(f"Current `toucDate`: {touchDate} is less than last updated `touchDate`: {self.__touchDate}")
            case _:
                pass
                
        self.__impression    += impression
        self.__click         += click   
        self.__expenditure   += expenditure
        self.__cpm           = (self.__expenditure / self.__impression) * 1000
        self.__ctr           = self.__click / self.__impression
        self.__touchDate     = touchDate
        self.__valuePerClick = 0 if self.__ctr == 0 else self.__cpm / (1000 * self.__ctr)