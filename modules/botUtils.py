from modules import FormatUtils, CalendarApi, contactUtils, DateUtils
import re
class Bot():
    def __init__(self):
        self.calendar = CalendarApi.CalendarAPI()

    def findEventByDateAndRegion(self, date, region):
        date = DateUtils.dayMonthToDateTime(date).date()
        eventList = self.calendar.listEvent()
        eventList = [x for x in eventList if region in x["summary"]]
        eventList = [x for x in eventList if date == x["start"].date()]
        return eventList[0]

    def isFull(self, date, region):
        event = self.findEventByDateAndRegion(date,region)
        if "FULL" in event["summary"]:
            return True
        else:
            return False

    def isAlreadySignedUp(self, date, region, email):
        event = self.findEventByDateAndRegion(date,region)
        for attendee in event["attendees"]:
            if email == attendee["email"]:
                return True
        return False


    def getEventsForTheWeek(self, date):
        eventList = self.calendar.listEvent()
        beginningOfWeek = DateUtils.getBeginningOfWeek(date)
        eventList = [x for x in eventList if x["start"].date() >= beginningOfWeek and "Available" not in x["summary"] and "Tier" in x["summary"] and x["end"].date() <= DateUtils.getEndOfWeek(date)]
        return eventList

    def isWaitList(self, date, region, email):
        sessionArray = []
        def createSessionString(eventArray):
            if len(eventArray) > 1:
                plural = "s"
            else: 
                plural = ""
            string = region + " session" + plural + " on "
            for event in range(0,len(eventArray)):
                dateString = DateUtils.rewriteDate(eventArray[event]["start"])
                if event == (len(eventArray) - 1) and len(eventArray) > 1:
                    string = string[:-2]
                    string += " and " + dateString + "."
                else:
                    string += dateString + ", "
            return string
        dateInDate = DateUtils.dayMonthToDateTime(date).date()
        within48Hours = DateUtils.isWithinTwoDays(dateInDate)
        if within48Hours:
            return (False,"")
        eventsForWeek = self.getEventsForTheWeek(dateInDate)
        eventsForRegion = [x for x in eventsForWeek if region in x["summary"]]
        for event in eventsForRegion:
            for attendee in event["attendees"]:
                if email == attendee["email"]:
                    sessionArray.append(event)
        if len(sessionArray) > 0:
            return (True, createSessionString(sessionArray))
        return (False,"")


    def getAvailability(self, message):
        availability = self.calendar.listEvents(True)
        messageArray = message.content.split(" ")
        if len(messageArray) > 2:
            dmName = messageArray[2]
            msg = FormatUtils.availabilityFormat(availability, dmName)
        else:
            msg = FormatUtils.availabilityFormat(availability)
        return msg

    def removeAvailability(self, date, region):
        availability = self.calendar.listEvents(True)
        dm = contactUtils.getRegion()[region][0].split(" ")[0]
        date = DateUtils.rewriteDate(DateUtils.dayMonthToDateTime(date))
        availability = [x for x in availability if dm in x[0] and x[1] == date]
        try:
            eventToRemove = availability[0][2]
        except:
            return True
        success = self.calendar.removeEvent(eventToRemove)
        if success[0] == True:
            return True
        else:
            return success[1]

    def printSessions(self, message):
        sessions = self.calendar.listEvents()
        msg = FormatUtils.sessionFormat(sessions)
        return msg

    def removeUser(self, message, name, admin=False):
        contactobj = contactUtils.getContacts()
        if admin:
            playerDict = {x:y for (x,y) in contactobj.items() if name in x}
            pattern = re.compile(".*removemem! " + name + ",")
        else:
            playerDict = {x:y for (x,y) in contactobj.items() if name in y}
            pattern = re.compile(".*remove!")
        fullName = list(playerDict)[0]
        email = playerDict[fullName][0]
        tempMessage = re.sub(pattern,"", message.content)
        messageArray = [x.strip() for x in tempMessage.split(",")]
        try:
            date, region = messageArray[0], messageArray[1]
        except:
            return (False, "Invalid")
        isAlreadySignedUp = self.isAlreadySignedUp(date,region,email)
        if not isAlreadySignedUp:
            return (False,"Empty")
        else:
            self.removeUserFromCalendar(fullName, date, region)
            return (True, [DateUtils.rewriteDate(DateUtils.dayMonthToDateTime(date)), region])

    def addUser(self, message, name, admin=False):
        contactobj = contactUtils.getContacts()
        if admin:
            playerDict = {x:y for (x,y) in contactobj.items() if name in x}
            pattern = re.compile(".*addmem! " + name + ",")
        else:
            playerDict = {x:y for (x,y) in contactobj.items() if name in y}
            pattern = re.compile(".*add!")
        fullName = list(playerDict)[0]
        email = playerDict[fullName][0]
        tempMessage = re.sub(pattern,"", message.content)
        messageArray = [x.strip() for x in tempMessage.split(",")]
        try:
            description, date, region = messageArray[0], messageArray[1], messageArray[2]
        except:
            return (False, "Invalid")
        try:
            isFull = self.isFull(date, region)
            isWaitList = self.isWaitList(date, region, email)
            isAlreadySignedUp = self.isAlreadySignedUp(date,region,email)
        except Exception as e:
            print(e)
            return (False, "Missing")
        if isAlreadySignedUp:
            return (False,"Double")
        if isFull:
            return (False, "Full")
        if isWaitList[0] == True:
            value = self.insertUserIntoCalendar(fullName, description, date, region, True)
            if value:
                return (True,isWaitList[1])
        else:
            value = self.insertUserIntoCalendar(fullName, description, date, region)
            return (True, "")
        
    def removeUserFromCalendar(self, personName, sessionDate, region):   
        def parseDescription(description):
            nonlocal personName
            individualNum = description.split("\n")
            firstName = personName.split(" ")[0]
            for item in range(0,len(individualNum)):
                if firstName in individualNum[item]:
                    individualNum[item] = individualNum[item][0:2]
            return "\n".join(individualNum)
        def increaseSeats(summary):
            summary = summary.split()
            if summary[0] == "FULL":
                summary[0] = "1"
                summary[1] = "Seat"
            else:
                summary[0] = str(int(summary[0]) + 1)
            return " ".join(summary)
        contactobj = contactUtils.getContacts()
        calendarEvent = self.findEventByDateAndRegion(sessionDate,region)
        email = contactobj[personName][0]
        calendarEvent["attendees"] = [x for x in calendarEvent["attendees"] if x["email"] != email]
        calendarEvent["description"] = parseDescription(calendarEvent["description"])
        calendarEvent["summary"] = increaseSeats(calendarEvent["summary"])
        del calendarEvent["start"]
        del calendarEvent["end"]
        value = self.calendar.updateEvent(calendarEvent)
        print(value)
        return value



    def insertUserIntoCalendar(self, personName, description, sessionDate, region, waitlist=False):
        def modifysummaryString(firstName, description):
            return firstName + " - " + description        
        def parseDescription(sessionDescription, characterDescription, waitlist):
            individualNum = sessionDescription.split("\n")
            if waitlist:
                individualNum.append(characterDescription)
            else:
                for num in range(0,len(individualNum)):
                    print(individualNum[num], len(individualNum[num]))
                    if len(individualNum[num]) > 10 or len(individualNum[num]) < 2:
                        continue
                    else:
                        print(characterDescription)
                        individualNum[num] += " " + characterDescription
                        break
            return "\n".join(individualNum)
        def reduceSeats(summary):
            summary = summary.split()
            summary[0] = str(int(summary[0])- 1)
            if int(summary[0]) == 1:
                summary[1] = "Seat"
            if int(summary[0]) == 0:
                summary[0] = "FULL"
                summary[1] = ""
            summary = " ".join(summary)
            return summary
        firstName = personName.split(" ")[0]
        characterDescription = modifysummaryString(firstName,description)
        contactList = contactUtils.getContacts()
        calendarEvent = self.findEventByDateAndRegion(sessionDate,region)
        calendarEvent["description"] = parseDescription(calendarEvent["description"], characterDescription, waitlist)
        if not waitlist:
            email = contactList[personName][0]
            calendarEvent['attendees'].append({"email":email})
            calendarEvent["summary"] = reduceSeats(calendarEvent["summary"])
        del calendarEvent["start"]
        del calendarEvent["end"]
        value = self.calendar.updateEvent(calendarEvent, waitlist)
        return value


    def createSession(self,message):
        pattern = re.compile(".*create!")
        tempMessage = re.sub(pattern,"", message.content)
        messageArray = [x.strip() for x in tempMessage.split(",")]
        date, startTime, endTime, summary, region, seshtype, difficulty, seats = messageArray[0],messageArray[1],messageArray[2],messageArray[3],messageArray[4],messageArray[5],messageArray[6],messageArray[7]
        eventobj = FormatUtils.formatNewEvent(date,startTime,endTime,summary,region,seshtype,difficulty,seats)
        availIsRemoved = self.removeAvailability(date,region)
        sessionAdded =  self.calendar.addEvent(eventobj)
        if availIsRemoved == True and sessionAdded[0] == True:
            return True
        else:
            msg = availIsRemoved + sessionAdded[1]
        return msg

    def getSessionsByUser(self, message, name):
        def sortByDate(elem):
            return elem["start"]
        contactobj = contactUtils.getContacts()
        playerDict = {x:y for (x,y) in contactobj.items() if name in y}

        events = self.calendar.listEvent()
        events = sorted([x for x in events if "Available" not in x["summary"]], key=sortByDate)
        events = [x for x in events if DateUtils.compareDate(x["start"])]
        print(events)
        print(playerDict)
        return ""
    