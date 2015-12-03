# -*- coding: utf-8 -*-
import datetime
from decorators import cache


@cache
def getDateOfWeek(year, index):
    date_first = datetime.datetime(year, 1, 1)
    calendar = date_first.isocalendar()
    if calendar[1] == 1:
        first = date_first - datetime.timedelta(days=calendar[2])
    else:
        first = date_first + datetime.timedelta(days=(6 - calendar[2]))
    dealta = (index - 1) * 7
    dates = [first + datetime.timedelta(days=dealta + i) for i in range(1, 8)]
    return dates
