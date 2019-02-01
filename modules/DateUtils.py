import datetime
import re

def dateTimeToReadableDate(datetimeobj):
    date = datetimeobj.strftime("%A, %B %d")
    day = int(date[-2:])
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return date + suffix

def datetimeToGameDate(dateTime, endTime):
    startTime = dateTime.strftime("%I:%M %p")
    endTime = endTime.strftime("%I:%M %p")
    return dateTime.strftime("%A, %m/%d ({startTime} - {endTime})".format(startTime=startTime,endTime=endTime))

def standardizeDate(start):
    if "date" in start:
        date = datetime.datetime.strptime(start["date"],"%Y-%m-%d")
    else:
        start["dateTime"] = re.sub("-05:00","",start["dateTime"])
        date = datetime.datetime.strptime(start["dateTime"],"%Y-%m-%dT%H:%M:%S")
    return date

def compareDate(date):
    today = datetime.datetime.today()
    return date > today

def rewriteDate(date):
    return dateTimeToReadableDate(date)

def formatEventDate(date):
    date = datetime.datetime.strptime(date,"%m/%d/%I:%M%p")
    date = date.replace(year=datetime.datetime.today().year)
    return date.strftime("%Y-%m-%dT%H:%M:%S")

def dayMonthToDateTime(dayMonth):
    month = int(dayMonth.split("/")[0])
    day = int(dayMonth.split("/")[1])
    year = datetime.datetime.today().year
    date = datetime.datetime(year,month,day)
    return date

def getBeginningOfWeek(date):
    weekday = date.weekday()
    if weekday == 6:
        return date
    else:
        return  date - datetime.timedelta(days=(weekday+1))


def getEndOfWeek(date):
    weekday = date.weekday()
    if weekday == 5:
        return date
    elif weekday == 6:
        return date + datetime.timedelta(days=weekday)
    else:
        return  date + datetime.timedelta(days=(5 - weekday))


def isWithinTwoDays(date):
    today = datetime.date.today()
    change = datetime.timedelta(days=2)
    twoDaysAhead = today + change
    return date <= twoDaysAhead