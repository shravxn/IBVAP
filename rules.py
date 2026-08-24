def loitering(duration_seconds, threshold_seconds=30):
    return duration_seconds >= threshold_seconds

def night_movement(hour, start=22, end=5):
    return hour >= start or hour < end
