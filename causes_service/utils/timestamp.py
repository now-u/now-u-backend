import time
import math
from datetime import datetime

def datetimeToTimestamp(input: datetime) -> int:
    return math.floor(time.mktime(input.timetuple()))
