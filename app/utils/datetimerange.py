from datetime import datetime

from pydantic import BaseModel


class DateTimeRange(BaseModel):
    start_datetime: datetime
    end_datetime: datetime


def is_valid_datetime_range(date_range: DateTimeRange) -> bool:
    return date_range.start_datetime < date_range.end_datetime