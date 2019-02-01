from modules import contactUtils, DateUtils


def availabilityFormat(availabilityList, filter=None):
    message = "\n\rHere is the availability for the following DMs: "
    if filter != None:
        availabilityList = [x for x in availabilityList if filter in x[0]]
        DMSet = [filter]
    else:
        DMSet = set()
        [DMSet.add(x[0].split(" ")[0]) for x in availabilityList]
        DMSet = sorted(list(DMSet))
    for dm in DMSet:
        message += dm + ", "
    message = message[:-2]
    for dm in DMSet:
        DMevents = [x for x in availabilityList if dm in x[0]]
        message += "\n\r" + "__**" + dm + "**__:\n\r"
        for event in DMevents:
            date = event[1]
            message += date + "\n\r"
        message += "\n\r"
    return message 

def sessionFormat(sessions):
    message = "```\n\rCurrently players have the ability to have Helper add and remove them from missions. If Helper is online, and you wish to have him add you to a session. type: \"@Helper add! (insert name/race/class, session date (in M\\D format), region)\"\n\rFor example: @Helper add! Azmorigan lvl 10 Cleric, 1/4, Far Reach\n\rTo have Helper remove you from a session. You must only give the date and region. @Helper remove! (date, region)\n\rFor example: @Helper remove! 1/4, Far Reach\n\rGRAB A SEAT!!\n"
    openSessions = [x for x in sessions if "FULL" not in x]
    closedSessions = [x for x in sessions if "FULL" in x]
    for session in openSessions:
        message += ":: " + session + "\n"
    message += "\n\rFULL\n"
    for session in closedSessions:
        message += ":: " + session + "\n"
    message += "\n\r"
    message += "Note: In general, games are first come, first served based on interest, etc. Joining a second, third, etc. game in each region requires the 48 hour window to ensure that others get a chance."
    message += "```"
    return message

def formatNewEvent(date, startTime, endTime, summary, region, seshtype, difficulty, seats):
    contactList = contactUtils.getContacts()
    regionObj = contactUtils.getRegion()
    startDate = DateUtils.formatEventDate(date + "/" + startTime)
    endDate = DateUtils.formatEventDate(date + "/" + endTime)
    summary = seats + " Seats - " + difficulty + " - " + summary + " - " + region +" ("+seshtype+")"
    owner = contactList[regionObj[region][0]][0]
    location = regionObj[region][1]
    attendees = [{"email":owner}]
    description = ""
    for seat in range(1,int(seats)+1):
        description += str(seat) + ".\n" 
    description += "\n\n\n\rWaitList:"
    finalFormat = {
        "start":{"dateTime":startDate+"-05:00"},
        "end":{"dateTime":endDate+"-05:00"},
        "summary":summary,
        "description":description,
        "attendees":attendees,
        "location":location,
        'reminders':{'useDefault': True}
    }
    return finalFormat

