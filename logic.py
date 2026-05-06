from datetime import datetime

DATE_FORMAT = "%Y-%m-%dT%H:%M"

def parse_dt(dt_str):
    return datetime.strptime(dt_str, DATE_FORMAT)

def calculate_mttr(detected_at, resolved_at):
    if not detected_at or not resolved_at:
        return None
    d = parse_dt(detected_at)
    r = parse_dt(resolved_at)
    if r < d:
        return None
    diff = r - d
    return round(diff.total_seconds() / 3600, 2)

def calculate_mttd(started_at, detected_at):
    if not started_at or not detected_at:
        return None
    s = parse_dt(started_at)
    d = parse_dt(detected_at)
    if d < s:
        return None
    diff = d - s
    return round(diff.total_seconds() / 3600, 2)

def get_severity_label(severity):
    labels = {
        "low": "Low",
        "medium": "Medium",
        "high": "High",
        "critical": "Critical"
    }
    return labels.get(severity.lower(), "Unknown")

def is_valid_incident(title, incident_type, started_at, detected_at):
    if not title or not incident_type or not started_at or not detected_at:
        return False, "All fields are required."
    try:
        s = parse_dt(started_at)
        d = parse_dt(detected_at)
    except ValueError:
        return False, "Invalid date format."
    if d < s:
        return False, "Detection time cannot be before start time."
    return True, "OK"

def format_hours(hours):
    if hours is None:
        return "N/A"
    total_minutes = int(hours * 60)
    h = total_minutes // 60
    m = total_minutes % 60
    return f"{h}h {m}m"