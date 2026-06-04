from typing import Any

def clean_telemetry(payload: dict[str, Any]) -> dict[str, Any]:
    """Clean and normalize telemetry data."""
    cleaned = payload.copy()
    
    # Null handling
    for key in ['temperature_c', 'pressure_psi', 'vibration_mm_s', 'power_consumption_kw']:
        if cleaned.get(key) is None:
            cleaned[key] = 0.0
            
    # Value clipping to prevent insane values
    if 'temperature_c' in cleaned:
        cleaned['temperature_c'] = max(-273.15, min(2000.0, float(cleaned['temperature_c'])))
        
    if 'pressure_psi' in cleaned:
        cleaned['pressure_psi'] = max(0.0, float(cleaned['pressure_psi']))
        
    if 'vibration_mm_s' in cleaned:
        cleaned['vibration_mm_s'] = max(0.0, float(cleaned['vibration_mm_s']))
        
    return cleaned
