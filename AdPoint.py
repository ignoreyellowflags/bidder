from datetime import datetime

class AdPoint:

    def __init__(
        self,
        accountId,
        adId,
        impression,
        click,
        cpm,
        touchDate
    ):
        
        self.__formatString = "%Y-%m-%d %H:%M:%S"
        
        assert isinstance(accountId, str), "Type Error. accountId must must be a string"
        self.accountId = accountId
        
        assert isinstance(adId, str), "Type Error. adId must must be a string"
        self.adId      = adId

        assert impression >= 0, "Value Error. Impressions number cannot be less than 0"
        self.impression = impression

        assert click >= 0, "Value Error. Clicks number cannot be less than 0"
        self.click   = click

        assert cpm   >= 0, "Value Error. CPM cannot be less than 0"
        self.cpm     = cpm

        touchDate      = datetime.strptime(touchDate, self.__formatString)
        self.touchDate = touchDate

    @property
    def formatString(self):
        return self.__formatString

    @property
    def meta(self):
        return {
            "accountId"   : self.accountId,
            "adId"        : self.adId,
            "impression"  : self.impression,
            "click"       : self.click,
            "ctr"         : self.__ctr(self.click, self.impression),
            "budgetSpent" : (self.cpm * self.impression) / 1000,
            "cpm"         : self.cpm,
            "cpc"         : (self.cpm * self.impression) / (1000 * self.click),
            "touchDate"   : self.touchDate
        }

    def __ctr(self, click, impression):
        
        match impression > 0:
            case True:
                return click / impression
            case _:
                return None