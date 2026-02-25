from calendar import timegm
from datetime import datetime,  timezone

def get_current_time()-> datetime:
    return datetime.now(timezone.utc)

def datetime_to_epoch(dt: datetime) -> int:
    return timegm(dt.utctimetuple())
