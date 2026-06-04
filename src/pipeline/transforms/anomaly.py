import math

def detect_z_score_anomaly(value: float, data: list[float], threshold: float = 3.0) -> bool:
    """Detect anomalies using Z-score."""
    if not data or len(data) < 2:
        return False
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    std_dev = math.sqrt(variance)
    if std_dev == 0:
        return False
    z_score = abs(value - mean) / std_dev
    return z_score > threshold

def detect_iqr_anomaly(value: float, data: list[float], multiplier: float = 1.5) -> bool:
    """Detect anomalies using Interquartile Range (IQR)."""
    if not data or len(data) < 4:
        return False
    sorted_data = sorted(data)
    n = len(sorted_data)
    q1 = sorted_data[n // 4]
    q3 = sorted_data[(3 * n) // 4]
    iqr = q3 - q1
    lower_bound = q1 - multiplier * iqr
    upper_bound = q3 + multiplier * iqr
    return value < lower_bound or value > upper_bound

def detect_cusum_anomaly(data: list[float], target: float, threshold: float, drift: float = 0.5) -> bool:
    """Detect anomalies using Cumulative Sum (CUSUM)."""
    pos_sum = 0.0
    neg_sum = 0.0
    
    for x in data:
        pos_sum = max(0.0, pos_sum + x - target - drift)
        neg_sum = max(0.0, neg_sum - x + target - drift)
        
        if pos_sum > threshold or neg_sum > threshold:
            return True
            
    return False
