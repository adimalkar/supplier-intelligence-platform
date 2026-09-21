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

def detect_modified_z_score_anomaly(value: float, data: list[float], threshold: float = 3.5) -> bool:
    """
    Detect anomalies using the Modified Z-score based on Median Absolute Deviation (MAD).
    Robust against extreme outlier masking where standard Z-score fails.
    """
    if not data or len(data) < 2:
        return False
        
    sorted_data = sorted(data)
    n = len(sorted_data)
    median = (sorted_data[n // 2] if n % 2 != 0 else (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2.0)
    
    # Calculate Median Absolute Deviation (MAD)
    abs_deviations = sorted(abs(x - median) for x in data)
    mad = (abs_deviations[n // 2] if n % 2 != 0 else (abs_deviations[n // 2 - 1] + abs_deviations[n // 2]) / 2.0)
    
    if mad == 0:
        return False
        
    # Constant 0.6745 represents 75th percentile of standard normal distribution
    modified_z = (0.6745 * abs(value - median)) / mad
    return modified_z > threshold

def detect_ewma_anomaly(data: list[float], alpha: float = 0.3, num_std: float = 3.0) -> list[int]:
    """
    Exponentially Weighted Moving Average (EWMA) control chart for time-series telemetry.
    Returns list of indices where sequential drift exceeded dynamic confidence bands.
    """
    if len(data) < 3:
        return []
        
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    std_dev = math.sqrt(variance)
    if std_dev == 0:
        return []
        
    anomalies: list[int] = []
    ewma = data[0]
    
    for i, x in enumerate(data):
        ewma = alpha * x + (1.0 - alpha) * ewma
        # Dynamic EWMA standard deviation control limits
        factor = math.sqrt((alpha / (2.0 - alpha)) * (1.0 - (1.0 - alpha) ** (2 * (i + 1))))
        upper_limit = mean + num_std * std_dev * factor
        lower_limit = mean - num_std * std_dev * factor
        
        if x > upper_limit or x < lower_limit:
            anomalies.append(i)
            
    return anomalies

