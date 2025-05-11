#!/bin/env python3
import os
import sys
from datetime import datetime, timedelta
import argparse

# defaults
IDLETIME_FILE = os.path.expanduser("~") + "/.idletimes"
MAX_BAR_LENGTH = 40
DAYS_TO_SHOW = 7
BAR_CHARACTER = "❙"  # 🬋❙
COLOR_DATES = "green"
COLOR_TIMES = "blue"
COLOR_BARS = "blue"
COLOR_IDLE_BARS = "lightgray"
DATE_FORMAT = "%b %d"
TIME_FORMAT = "%H:%M"
SECONDS_PER_BAR = "auto"
WITH_IDLETIMES = False
CURRENT_TIME = datetime.now()


def printTime(dayStr, durationWithIdletime, idletimeSeconds):
    netDuration = durationWithIdletime - timedelta(seconds=idletimeSeconds)
    if WITH_IDLETIMES:
        if durationWithIdletime.days == 1:
            formattedTimeStr = "24h 00m"
        else:
            formattedTimeStr = f"{f'{durationWithIdletime.total_seconds() // 3600:.0f}': >2}h {f'{durationWithIdletime.total_seconds() //60 % 60:.0f}': >2}m"
    else:
        if netDuration.days == 1:
            formattedTimeStr = "24h 00m"
        else:
            formattedTimeStr = f"{f'{netDuration.total_seconds() // 3600:.0f}': >2}h {f'{netDuration.total_seconds() //60 % 60:.0f}': >2}m"

    print(
        colored(dayStr, COLOR_DATES)
        + " "
        + bold(colored(formattedTimeStr, COLOR_TIMES))
        + " "
        + (
            colored(
                BAR_CHARACTER * int(netDuration.total_seconds() // SECONDS_PER_BAR),
                COLOR_BARS,
            )
            if SECONDS_PER_BAR
            else ""
        )
        + (
            colored(
                BAR_CHARACTER * int(idletimeSeconds // SECONDS_PER_BAR),
                COLOR_IDLE_BARS,
            )
            if SECONDS_PER_BAR and WITH_IDLETIMES
            else ""
        )
    )


def bold(text):
    return f"\033[1m{text}\033[00m"


def colored(text, color):
    if color == "red":
        return f"\033[91m{text}\033[00m"
    elif color == "green":
        return f"\033[92m{text}\033[00m"
    elif color == "yellow":
        return f"\033[93m{text}\033[00m"
    elif color == "blue":
        return f"\033[94m{text}\033[00m"
    elif color == "purple":
        return f"\033[95m{text}\033[00m"
    elif color == "cyan":
        return f"\033[96m{text}\033[00m"
    elif color == "lightgray":
        return f"\033[97m{text}\033[00m"
    else:
        return text


def updateIdleTime(file, idleTime, idleDate):
    idleTimesList = []
    file.seek(0)
    idleTimeToUpdate_str = file.readline()
    idleTimesList.append(idleTimeToUpdate_str)
    idleTimeToUpdate_split = idleTimeToUpdate_str.split(" - ")
    idleDateToUpdate_obj = datetime.strptime(
        idleTimeToUpdate_split[0] + CURRENT_TIME.strftime("%Y"), DATE_FORMAT + "%Y"
    ).date()
    while idleDateToUpdate_obj > idleDate:
        idleTimeToUpdate_str = file.readline()
        if not idleTimeToUpdate_str:
            idleDateToUpdate_obj = None
            break
        idleTimesList.append(idleTimeToUpdate_str)
        idleTimeToUpdate_split = idleTimeToUpdate_str.split(" - ")
        idleDateToUpdate_obj = datetime.strptime(
            idleTimeToUpdate_split[0] + CURRENT_TIME.strftime("%Y"), DATE_FORMAT + "%Y"
        ).date()

    if idleDateToUpdate_obj != idleDate:
        createIdleTime(file, idleTime, idleDate)

    idleTimeToUpdate_obj = timedelta(
        hours=int(idleTimeToUpdate_split[1].split(":")[0]),
        minutes=int(idleTimeToUpdate_split[1].split(":")[1]),
    )

    newIdleTime_obj = idleTimeToUpdate_obj + idleTime
    if newIdleTime_obj.days > 0:
        print("Invalid/Impossible idletime, skipping update")
        sys.exit(1)

    newIdleTime_split = str(newIdleTime_obj).split(":")
    newIdleTimeStr = newIdleTime_split[0].zfill(2) + ":" + newIdleTime_split[1]
    print(
        "Updating idletime for",
        idleDate.strftime(DATE_FORMAT),
        "to " + newIdleTimeStr,
    )

    file.seek(0)
    idleTimesList[-1] = idleDate.strftime(DATE_FORMAT) + " - " + newIdleTimeStr + "\n"
    file.writelines(idleTimesList)


def createIdleTime(file, idleTime, idleDate):
    file.seek(0)
    idleDatesTimes = file.readlines()

    if idleTime.days == 1:
        newIdleTimeStr = "23:59"
    else:
        newIdleTime_split = str(idleTime).split(":")
        newIdleTimeStr = newIdleTime_split[0].zfill(2) + ":" + newIdleTime_split[1]

    newIdleDateTimeStr = f"{idleDate.strftime(DATE_FORMAT)} - {newIdleTimeStr}"

    insertionIndex = -1
    for i, idleDateTime in enumerate(idleDatesTimes):
        if idleDateTime:
            idleDate_obj = datetime.strptime(
                idleDateTime.split(" - ")[0] + CURRENT_TIME.strftime("%Y"),
                DATE_FORMAT + "%Y",
            ).date()
            if idleDate_obj < idleDate:
                insertionIndex = i
                break
    idleDatesTimes.insert(insertionIndex, newIdleDateTimeStr + "\n")
    print(
        "Creating new idletime for ",
        idleDate.strftime(DATE_FORMAT),
        ": " + newIdleTimeStr,
    )

    file.seek(0)
    file.writelines(idleDatesTimes)


def addIdleTimeToFile(idleTime_seconds, idleDate=CURRENT_TIME.date()):
    idleTime = timedelta(seconds=idleTime_seconds)
    if idleDate == CURRENT_TIME.date():
        elapsedTimeForIdleDate = timedelta(
            hours=CURRENT_TIME.hour, minutes=CURRENT_TIME.minute
        )
    else:
        elapsedTimeForIdleDate = timedelta(hours=24)

    idleTimeForPreviousDay = idleTime - elapsedTimeForIdleDate

    # print("For ", idleDate.strftime(DATE_FORMAT))
    # print("Idle time:", idleTime)
    # print("Elapsed time:", elapsedTimeForIdleDate)
    # print("Idle time for previous day:", idleTimeForPreviousDay)

    if idleTimeForPreviousDay > timedelta(0):
        print("Idletime for previous day detected, splitting...")
        addIdleTimeToFile(
            idleTimeForPreviousDay.total_seconds(), idleDate - timedelta(days=1)
        )
        idleTime = elapsedTimeForIdleDate
    with open(IDLETIME_FILE, "r+") as file:
        latestIdleStr = file.readline()
        if latestIdleStr:
            latestIdleDate_obj = datetime.strptime(
                latestIdleStr.split(" - ")[0] + CURRENT_TIME.strftime("%Y"),
                DATE_FORMAT + "%Y",
            ).date()
        else:
            createIdleTime(file, idleTime, idleDate)
            return
        if latestIdleDate_obj >= idleDate:
            updateIdleTime(file, idleTime, idleDate)
        else:
            createIdleTime(file, idleTime, idleDate)


def parseArgs():
    global IDLETIME_FILE, MAX_BAR_LENGTH, BAR_CHARACTER, DAYS_TO_SHOW, WITH_IDLETIMES
    parser = argparse.ArgumentParser(description="Show screen time for the last n days")
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        nargs="?",
        help="Number of days to show screen time for (default: %(default)d)",
        default=DAYS_TO_SHOW,
    )
    parser.add_argument(
        "-i",
        "--with-idletimes",
        help="Also show idle times",
        action="store_true",
    )
    parser.add_argument(
        "-s",
        "--style",
        type=int,
        help="Style for bar character (1-9) (default: 1)",
        default=1,
        metavar="NUMBER(1-9)",
    )
    parser.add_argument(
        "-m",
        "--max-length",
        type=int,
        help="Specify length of longest bar to auto adjust other bars relatively (default: %(default)d)",
        default=MAX_BAR_LENGTH,
        metavar="LENGTH",
    )
    parser.add_argument(
        "-f",
        "--idletime-file",
        type=argparse.FileType("a+"),
        help="Specify the file to read/write idletimes (default: %(default)s)",
        default=IDLETIME_FILE,
        metavar="FILE",
    )
    parser.add_argument(
        "-a",
        "--add-idletime",
        type=int,
        help="Add idle time for today (in seconds)",
        metavar="SECONDS",
    )
    args = parser.parse_args()

    if args.add_idletime:
        addIdleTimeToFile(args.add_idletime)
        sys.exit(0)

    IDLETIME_FILE = args.idletime_file.name
    MAX_BAR_LENGTH = args.max_length
    DAYS_TO_SHOW = args.days
    WITH_IDLETIMES = args.with_idletimes

    match args.style:
        case 1:
            BAR_CHARACTER = "❙"
        case 2:
            BAR_CHARACTER = "🬋"
        case 3:
            BAR_CHARACTER = "▆"
        case 4:
            BAR_CHARACTER = "❘"
        case 5:
            BAR_CHARACTER = "❚"
        case 6:
            BAR_CHARACTER = "█"
        case 7:
            BAR_CHARACTER = "━"
        case 8:
            BAR_CHARACTER = "▭"
        case 9:
            BAR_CHARACTER = "╼"


def updateTimePerDayDict(timePerDayDict, rebootDateObj, rebootDuration):
    rebootDurationWithoutDays = timedelta(
        hours=rebootDuration.seconds // 3600, minutes=rebootDuration.seconds // 60 % 60
    )
    if rebootDuration.days > 0:
        for i in range(1, rebootDuration.days + 1):
            timePerDayDict[(rebootDateObj + timedelta(days=i))] = timedelta(days=1)
    try:
        timePerDayDict[rebootDateObj] += rebootDurationWithoutDays
    except KeyError:
        timePerDayDict[rebootDateObj] = rebootDurationWithoutDays


def fillMissingDaysWithZeroTime(timePerDayDict, rebootDateObj):
    if rebootDateObj not in timePerDayDict:
        latestZeroTimeDay = rebootDateObj + timedelta(days=1)
        oldestZeroTimeDay = latestZeroTimeDay
        while (
            oldestZeroTimeDay not in timePerDayDict
            and oldestZeroTimeDay <= CURRENT_TIME.date()
        ):
            oldestZeroTimeDay += timedelta(days=1)
        for i in range(1, (oldestZeroTimeDay - latestZeroTimeDay).days + 1):
            if len(timePerDayDict) == DAYS_TO_SHOW:
                return
            updateTimePerDayDict(
                timePerDayDict, oldestZeroTimeDay - timedelta(days=i), timedelta(0)
            )


def handleRunningRebootLine(latestRunningRebootLine, timePerDayDict):
    runningRebootDateStr = " ".join(latestRunningRebootLine[5:7])
    runningRebootDateStr = runningRebootDateStr[:4] + runningRebootDateStr[4:].zfill(2)
    runningRebootDateObj = datetime.strptime(
        runningRebootDateStr + str(CURRENT_TIME.year), "%b %d%Y"
    ).date()
    rebootTime = datetime.strptime(
        f"{latestRunningRebootLine[-3]} {runningRebootDateStr} {CURRENT_TIME.year}",
        "%H:%M %b %d %Y",
    )
    updateTimePerDayDict(
        timePerDayDict, runningRebootDateObj, CURRENT_TIME - rebootTime
    )


def parseRebootLogs():
    rebootOutput = os.popen("last reboot")
    rebootLine = rebootOutput.readline()[:-1]
    timePerDayDict = {}
    latestRunningRebootLine = None

    while rebootLine:
        rebootLine = rebootLine.split()
        rebootDateStr = " ".join(rebootLine[5:7])
        rebootDateStr = rebootDateStr[:4] + rebootDateStr[4:].zfill(2)
        rebootDateObj = datetime.strptime(
            rebootDateStr + str(CURRENT_TIME.year), "%b %d%Y"
        ).date()

        if rebootDateObj not in timePerDayDict and len(timePerDayDict) > DAYS_TO_SHOW:
            return timePerDayDict

        fillMissingDaysWithZeroTime(timePerDayDict, rebootDateObj)

        if len(rebootLine) < 3:
            break
        if rebootLine[-1] == "running":
            latestRunningRebootLine = rebootLine
            rebootLine = rebootOutput.readline()
            continue

        if latestRunningRebootLine:
            handleRunningRebootLine(latestRunningRebootLine, timePerDayDict)
            latestRunningRebootLine = None

        try:
            # (HH:MM)
            rebootTimeObj = datetime.strptime(rebootLine[-1], "(%H:%M)")
            rebootDuration = timedelta(
                hours=rebootTimeObj.hour,
                minutes=rebootTimeObj.minute,
            )
        except ValueError:
            try:
                # (DD+HH:MM)
                rebootTimeObj = datetime.strptime(
                    f"{rebootLine[-1][1:-1].zfill(8)} {CURRENT_TIME.year}",
                    "%d+%H:%M %Y",
                )
                rebootDuration = timedelta(
                    days=rebootTimeObj.day,
                    hours=rebootTimeObj.hour,
                    minutes=rebootTimeObj.minute,
                )
            except ValueError:
                # weird durations like (-HH:MM)
                rebootDuration = timedelta(0)

        updateTimePerDayDict(timePerDayDict, rebootDateObj, rebootDuration)
        rebootLine = rebootOutput.readline()[:-1]

    return timePerDayDict


def parseIdleTimes(timePerDayDict):
    try:
        with open(IDLETIME_FILE, "r") as file:
            idletimesDict = {}
            idletimes = file.read().split("\n")
            for idletime in idletimes:
                if idletime:
                    idletime = idletime.split(" - ")
                    idleDateStr = idletime[0].strip()
                    idleDateObj = datetime.strptime(
                        idleDateStr + str(CURRENT_TIME.year), DATE_FORMAT + "%Y"
                    ).date()
                    if (
                        idleDateObj not in timePerDayDict
                        and len(timePerDayDict) == DAYS_TO_SHOW
                    ):
                        break
                    idletimeObj = datetime.strptime(idletime[1], TIME_FORMAT)
                    idletimeObj = timedelta(
                        hours=idletimeObj.hour, minutes=idletimeObj.minute
                    )
                    idletimesDict[idleDateObj] = idletimeObj
    except FileNotFoundError:
        print(colored(bold("No idletime file found"), "red"))
        idletimesDict = {}
    return idletimesDict


def getSecondsPerBar(timePerDayDict, idletimesDict):
    maxTime = timedelta(0)
    count = 0
    for day in timePerDayDict:
        count += 1
        if count > DAYS_TO_SHOW:
            break
        netDuration = timePerDayDict[day] - (
            timedelta(0) if WITH_IDLETIMES else (idletimesDict.get(day, timedelta(0)))
        )
        if netDuration > maxTime:
            maxTime = netDuration
    return maxTime.total_seconds() / MAX_BAR_LENGTH


def printAllDays(timePerDayDict, idletimesDict):
    count = 0
    for day in timePerDayDict:
        count += 1
        if count > DAYS_TO_SHOW:
            break
        printTime(
            day.strftime(DATE_FORMAT),
            timePerDayDict[day],
            idletimesDict.get(day, timedelta(0)).total_seconds(),
        )


def getTotalTimeAndDays(timePerDayDict, idletimesDict):
    totalTime = timedelta(0)
    numOfDays = 0
    for day in timePerDayDict:
        numOfDays += 1
        if numOfDays > DAYS_TO_SHOW:
            break
        totalTime += timePerDayDict[day] - (
            timedelta(0) if WITH_IDLETIMES else idletimesDict.get(day, timedelta(0))
        )
    return totalTime, numOfDays - 1


def printTotalTime(totalTime, numOfDays):
    print(
        colored("Total (", "cyan")
        + colored(numOfDays, COLOR_TIMES)
        + colored(" days): ", "cyan")
        + bold(
            colored(
                f"{str(totalTime.days)+'d ' if totalTime.days else ''}{totalTime.seconds // 3600}h {totalTime.seconds // 60 % 60}m",
                "yellow",
            )
        )
        + (
            colored(" (including idle times): ", COLOR_DATES)
            if WITH_IDLETIMES
            else colored(": ", COLOR_DATES)
        )
    )


def printAverageTime(timePerDayDict, totalTime):
    avgTime = totalTime / len(timePerDayDict)
    print(
        colored("Average: ", "cyan")
        + bold(
            colored(
                f"{str(avgTime.days)+'d ' if avgTime.days else ''}{avgTime.seconds // 3600}h {avgTime.seconds // 60 % 60}m",
                "yellow",
            )
        )
    )


def main():
    global SECONDS_PER_BAR

    parseArgs()
    timePerDayDict = parseRebootLogs()
    idletimesDict = parseIdleTimes(timePerDayDict)
    if SECONDS_PER_BAR == "auto":
        SECONDS_PER_BAR = getSecondsPerBar(timePerDayDict, idletimesDict)
    printAllDays(timePerDayDict, idletimesDict)
    totalTime, numOfDays = getTotalTimeAndDays(timePerDayDict, idletimesDict)
    printTotalTime(totalTime, numOfDays)
    printAverageTime(timePerDayDict, totalTime)


if __name__ == "__main__":
    main()
