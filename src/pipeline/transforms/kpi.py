def calculate_oee(availability: float, performance: float, quality: float) -> float:
    """Calculate Overall Equipment Effectiveness (OEE)."""
    return availability * performance * quality

def calculate_cpk(data: list[float], usl: float, lsl: float) -> float:
    """Calculate the Process Capability Index (Cpk)."""
    if not data or len(data) < 2:
        return 0.0
    import math
    mean = sum(data) / len(data)
    variance = sum((x - mean) ** 2 for x in data) / (len(data) - 1)
    std_dev = math.sqrt(variance)
    if std_dev == 0:
        return 0.0
    cpk_upper = (usl - mean) / (3 * std_dev)
    cpk_lower = (mean - lsl) / (3 * std_dev)
    return min(cpk_upper, cpk_lower)

def calculate_yield_trend(yields: list[float]) -> float:
    """Calculate simple linear trend of yields over time (slope)."""
    if not yields or len(yields) < 2:
        return 0.0
    n = len(yields)
    sum_x = sum(range(n))
    sum_y = sum(yields)
    sum_xy = sum(x * y for x, y in enumerate(yields))
    sum_xx = sum(x * x for x in range(n))
    
    denominator = (n * sum_xx - sum_x * sum_x)
    if denominator == 0:
        return 0.0
    
    slope = (n * sum_xy - sum_x * sum_y) / denominator
    return slope

def detect_yield_shift(yields: list[float], window_size: int = 5, threshold: float = 0.05) -> bool:
    """Detect if there is a sudden shift in average yield between two adjacent windows."""
    if len(yields) < window_size * 2:
        return False
    recent_window = yields[-window_size:]
    previous_window = yields[-2 * window_size : -window_size]
    
    recent_avg = sum(recent_window) / window_size
    previous_avg = sum(previous_window) / window_size
    
    return abs(recent_avg - previous_avg) > threshold
