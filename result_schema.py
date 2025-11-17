from enum import Enum
import pydantic

class DurationUnit(str, Enum):
	sec = "sec"
	ms = "ms"
	us = "us"
	ns = "ns"

class PyperfResult(pydantic.BaseModel):
	Test: str = pydantic.Field(description="Name of the test that was ran")
	Avg: float = pydantic.Field(description="Duration, unit is determined by duration_unit field", allow_inf_nan=False, gt=0)
	Unit: DurationUnit = pydantic.Field(description="Unit of duration")