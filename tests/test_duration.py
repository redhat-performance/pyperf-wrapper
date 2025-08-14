from pathlib import Path
import pydantic
import sys
import pytest

file = Path(__file__).resolve()
parent = file.parent.parent
sys.path.append(str(parent))

from result_schema import PyperfResult, DurationUnit

@pytest.mark.parametrize("duration", [
		"-12", "0", "0.0", "inf", "nan",
		"abc", "123abc", "123abc", "12abc34",
		"123.123.123", "-0", "-0.0", "-inf", "-nan"
	])
def test_duration_invalid(duration):
	with pytest.raises(pydantic.ValidationError):
		PyperfResult(Test="test", Avg=duration, Unit=DurationUnit.sec)

@pytest.mark.parametrize("duration", [
	"123", "123.456", "0.000001", "0.000000001", "1234567890", "1234567890.1234567890"
])
def test_duration_valid(duration):
	result = PyperfResult(Test="test", Avg=duration, Unit=DurationUnit.sec)
	assert result.Avg == float(duration)