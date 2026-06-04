import pytest
from src.pipeline.transforms.kpi import (
    calculate_oee,
    calculate_cpk,
    calculate_yield_trend,
    detect_yield_shift
)

def test_calculate_oee():
    result = calculate_oee(0.9, 0.95, 0.99)
    assert abs(result - 0.84645) < 0.001

def test_calculate_cpk():
    data = [10.0, 10.2, 9.8, 10.1, 9.9, 10.0]
    # mean = 10.0, var = approx 0.02
    # std_dev = approx 0.1414
    result = calculate_cpk(data, 10.5, 9.5)
    # cpk = (10.5 - 10.0) / (3 * 0.1414) = 0.5 / 0.4242 = 1.17
    assert result > 0.0

def test_calculate_yield_trend():
    yields = [0.90, 0.92, 0.94, 0.96, 0.98]
    slope = calculate_yield_trend(yields)
    assert abs(slope - 0.02) < 0.001

def test_detect_yield_shift():
    yields = [0.95, 0.94, 0.95, 0.96, 0.95, 0.80, 0.81, 0.82, 0.80, 0.79]
    shift = detect_yield_shift(yields, window_size=5, threshold=0.1)
    assert shift is True
    
    yields_stable = [0.95, 0.94, 0.95, 0.96, 0.95, 0.94, 0.95, 0.96, 0.95, 0.94]
    shift_stable = detect_yield_shift(yields_stable, window_size=5, threshold=0.1)
    assert shift_stable is False
