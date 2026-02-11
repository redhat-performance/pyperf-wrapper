import pydantic
import datetime

class PyperfResults(pydantic.BaseModel):
    Test: str #todo make an enum
    Avg: float = pydantic.Field(gt=0, allow_inf_nan=False)
    Unit: str #todo make an enum
    Start_Date: datetime.datetime
    End_Date: datetime.datetime
