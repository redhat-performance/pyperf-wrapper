from pathlib import Path
import pydantic
import sys
import pytest

file = Path(__file__).resolve()
parent = file.parent.parent
sys.path.append(str(parent))

from result_schema import PyperfResult, DurationUnit

@pytest.mark.parametrize("duration_unit", [
		"MS", "Day", "Year", "Hour", "cat", "dog",
		"123", "-12034"
	])
def test_duration_unit_invalid(duration_unit):
	with pytest.raises(pydantic.ValidationError):
		PyperfResult(Test="test", Avg=12, Unit=duration_unit)

@pytest.mark.parametrize("duration_unit", [
		DurationUnit.sec, DurationUnit.ms, DurationUnit.us, DurationUnit.ns,
		"sec", "ms", "us", "ns"
	])
def test_duration_unit_invalid(duration_unit):
	result = PyperfResult(Test="test", Avg=12, Unit=duration_unit)
	assert result.Unit == duration_unit
