from Advertisment.Ad import Ad
from datetime import datetime, time
from datetime import timedelta
from typing   import Optional, Generator
import math

class Scheduler:

    def __init__(
        self,
        dateStart: datetime,
        dateEnd  : datetime
    ):

        self.__dateStart     = dateStart
        self.__dateEnd       = dateEnd
        
        self.__secondsInHour = 3600

        self.__weekEnd  : list[int] = list(range(5,7))
    @property
    def dateStart(self):
        return self.__dateStart
    @property
    def dateEnd(self):
        return self.__dateEnd
    @property
    def getBorder(self):
         return (self.__dateStart, self.__dateEnd)  
    @property
    def duration(self) -> int:

        duration = int( (self.__dateEnd - self.__dateStart).total_seconds() / self.__secondsInHour)

        return duration


    def getRange(self, freq: str) -> Generator[datetime, None, None]:

        freq = self.__freqParsing(freq)

        initDate       = self.__dateStart
        while initDate <= self.__dateEnd:
            
            yield initDate
            initDate   += timedelta(hours=freq)

    def __freqParsing(self, freq: str) -> float:

        match freq:
            case 'half-hour':
                return 0.5
            case '1hour':
                return 1.0
            case _:
                raise ValueError("Invalid `freq` value. Use `half-hour` or `1hour` values.")

    def nightMode(self, mode: str) -> tuple[int]:

        match mode:
            case 'early':
                return (20, 8)
            case 'standard':
                return (22,8) 
            case 'late':
                return (0, 8)
            case _:
                raise ValueError("Invalid `mode` value. Use `early`, `standard` or `late` values.")

    def isWeekEnd(self, touchDate: datetime) -> bool:

        return True if touchDate.weekday() in self.__weekEnd else False

    def isNightHour(self, touchDate: datetime, mode: str) -> bool:

        touchTime = touchDate.time()
        nightTime = self.nightMode(mode)

        t1, t2    = ( time(nightTime[0]), time(nightTime[1]) )
        
        match (t1 >= t2):
            case True:
                return not ( (touchTime >= t1) or (touchTime < t2) )
            case _:
                return (t1 <= touchTime < t2)

class Bidder(Scheduler):

    def __init__(
        self                 ,
        ad             : Ad  ,
        cpm            : tuple[float]
    ):
        super().__init__(ad.dateStart, ad.dateEnd)
        self.__ad      = ad
        self.__cpm     = cpm

        self.__epsilon = 0.01

    def update(self, impression: int, click: int, expenditure: float, touchDate: str) -> None:

        self.__ad.update(
            impression  = impression,
            click       = click,
            expenditure = expenditure,
            touchDate   = touchDate
        )


    @property
    def Ui(self):
        return self.__ad.valuePerClick * self.__ad.ctr

    def pace(
        self                                  ,
        weekEndTimeOffActivity: bool          ,
        nightTimeOffActivity  : Optional[str] ,
        freq                  : str
    ) -> tuple[float]:
        
        i              = 0
        touchDateIndex = None
        observation    = self.getRange(freq = freq)

        for date in observation:

            isBannedDay  = False if (weekEndTimeOffActivity == False) else self.isWeekEnd(date)
            isBannedHour = False if (nightTimeOffActivity == None)    else self.isNightHour(date, nightTimeOffActivity)

            match ( (touchDateIndex == None) and (date >= self.__ad.touchDate )): #instead of == use >=
                case True:
                    touchDateIndex = i
                case _:
                    pass


            match (isBannedHour or isBannedDay):
                case True:
                    pass
                    
                case _ :
                    match (date == self.dateEnd):
                        case True:
                            pass
                        case _:
                            i += 1

        return (round(touchDateIndex / i, 5), touchDateIndex, i) # pace (share), absolute index, active periods

    def expenditurePlan(
        self,
        budget                : float        ,
        weekEndTimeOffActivity: bool         ,
        nightTimeOffActivity  : Optional[str],
        freq                  : str) -> float:

        pace, _, _ = self.pace(
            weekEndTimeOffActivity = weekEndTimeOffActivity,
            nightTimeOffActivity   = nightTimeOffActivity,
            freq                   = freq
        )

        return pace * budget

    
    def roi(
        self,
        expenditurePlan : float
    ) -> float:

        gain = self.__ad.valuePerClick * self.__ad.click
        
        match expenditurePlan == 0:
            case True:
                roi = 0
            case _:
                roi  = (gain - expenditurePlan) / expenditurePlan

        return roi
    

    def Ri(
        self       ,
        roi : float,
          ) -> float:
    
        return max(0.0001, min(1, 1 / (roi + 1) ) )


    def bidPace(
        self,
        budget                : float        ,
        weekEndTimeOffActivity: bool         ,
        nightTimeOffActivity  : Optional[str],
        freq                  : str) -> dict[str,float]:

        expenditurePlan = self.expenditurePlan(
            budget=budget,
            weekEndTimeOffActivity = weekEndTimeOffActivity,
            nightTimeOffActivity   = nightTimeOffActivity,
            freq                   = freq
        )

        roi = self.roi(expenditurePlan=expenditurePlan)
        Ri  = self.Ri(roi=roi)
        
        match self.__ad.expenditure < expenditurePlan:
            case True:
                bid = Ri * math.e ** self.__epsilon
            case _:
                bid = Ri * math.e ** (- self.__epsilon)
                
        cpm     = bid * self.Ui * 1000
        cpmCond = max(self.__cpm[0], min(self.__cpm[1], cpm))

        return {
            'cpm'             : cpm,
            'cpmCond'         : cpmCond,
            'expenditurePlan' : expenditurePlan,
            'expenditure'     : self.__ad.expenditure,
            'expenditureGap'  : expenditurePlan - self.__ad.expenditure,
            'expenditureGap%' : round( (expenditurePlan - self.__ad.expenditure ) / expenditurePlan, 2),
            'roi'             : roi,
            'Ri'              : Ri,
            'bid'             : bid,
            'Ui'              : self.Ui
        }