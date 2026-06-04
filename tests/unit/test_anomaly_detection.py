import pytest
from src.pipeline.transforms.anomaly import (
    detect_z_score_anomaly,
    detect_iqr_anomaly,
    detect_cusum_anomaly
)

def test_detect_z_score_anomaly():
    data = [10.0] * 50
    data.append(10.1) # inject small noise
    # mean ~10, very small std_dev
    
    assert detect_z_score_anomaly(100.0, data, threshold=3.0) is True
    assert detect_z_score_anomaly(10.0, data, threshold=3.0) is False

def test_detect_iqr_anomaly():
    data = [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0]
    
    # 25th percentile ~ 3, 75th percentile ~ 8, IQR ~ 5
    # bounds: 3 - 1.5*5 = -4.5, 8 + 1.5*5 = 15.5
    
    assert detect_iqr_anomaly(20.0, data, multiplier=1.5) is True
    assert detect_iqr_anomaly(5.0, data, multiplier=1.5) is False

def test_detect_cusum_anomaly():
    data_normal = [10.0, 10.1, 9.9, 10.0, 10.0]
    assert detect_cusum_anomaly(data_normal, target=10.0, threshold=5.0) is False
    
    data_anomaly = [10.0, 10.1, 15.0, 16.0, 15.0]
    assert detect_cusum_anomaly(data_anomaly, target=10.0, threshold=5.0) is True
