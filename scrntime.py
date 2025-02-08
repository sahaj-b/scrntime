#!/bin/env python3
import os
import sys
from datetime import datetime, timedelta
import argparse

# defaults
IDLETIME_FILE = os.path.expanduser("~") + "/.idletimes"
MAX_BAR_LENGTH = 40
BAR_CHARACTER = "❙"  # 🬋❙
COLOR_DATES = "green"
COLOR_TIMES = "blue"
COLOR_BARS = "blue"
COLOR_IDLE_BARS = "lightgray"


def printTime(day, netTime, idletime_seconds):
    formattedTime_split = str(netTime).split(":")
    formattedTimeStr = f"{f'{formattedTime_split[0]}': >2}h {formattedTime_split[1]}m"
    netTimeWithoutIdle = netTime - timedelta(seconds=idletime_seconds)
    print(
        colored(day, COLOR_DATES)
        + " "
        + bold(colored(formattedTimeStr, COLOR_TIMES))
        + " "
        + colored(
            BAR_CHARACTER * int(netTimeWithoutIdle.total_seconds() // SECONDS_PER_BAR),
            COLOR_BARS,
        )
        + colored(
            BAR_CHARACTER * int(idletime_seconds // SECONDS_PER_BAR),
            COLOR_IDLE_BARS,
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


def updateIdleTime(file, latestIdleDateTime, currentIdleTime):
    latestIdleTime_obj = timedelta(
        hours=int(latestIdleDateTime[1].split(":")[0]),
        minutes=int(latestIdleDateTime[1].split(":")[1]),
    )
    newIdleTime_split = str(latestIdleTime_obj + currentIdleTime).split(":")
    newIdleTimeStr = newIdleTime_split[0].zfill(2) + ":" + newIdleTime_split[1]
    print(f"Updated idletime from {latestIdleDateTime[1][:-1]} to {newIdleTimeStr}")

    file.seek(0)
    file.write(latestIdleDateTime[0] + " - " + newIdleTimeStr + "\n")


def createIdleTime(file, currentIdleTime):
    file.seek(0)
    idleDatesTimes = file.readlines()
    newIdleTime_split = str(currentIdleTime).split(":")
    newIdleTimeStr = newIdleTime_split[0].zfill(2) + ":" + newIdleTime_split[1]
    newIdleDateTimeStr = f"{datetime.now().strftime('%b %d')} - {newIdleTimeStr}"
    idleDatesTimes.insert(0, newIdleDateTimeStr + "\n")
    print("Creating new idletime: " + newIdleTimeStr)
    file.seek(0)
    file.writelines(idleDatesTimes)


def addIdleTimeToFile(seconds):
    currentIdleTime = timedelta(seconds=seconds)
    with open(IDLETIME_FILE, "r+") as file:
        latestIdleStr = file.readline()
        if latestIdleStr:
            latestIdleDateTime = latestIdleStr.split(" - ")
        else:
            latestIdleDateTime = [-1, -1]

        if latestIdleDateTime[0] == datetime.now().strftime("%b %d"):
            updateIdleTime(file, latestIdleDateTime, currentIdleTime)
        else:
            createIdleTime(file, currentIdleTime)


def parseArgs():
    parser = argparse.ArgumentParser(description="Show screen time for the last n days")
    parser.add_argument(
        "-d",
        "--days",
        type=int,
        nargs="?",
        help="Number of days to show screen time for (default: %(default)d)",
        default=7,
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
    return args


args = parseArgs()
if args.add_idletime:
    addIdleTimeToFile(args.add_idletime)
    sys.exit(0)

IDLETIME_FILE = args.idletime_file.name
MAX_BAR_LENGTH = args.max_length

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

daysToShow = args.days

# reading reboot times
rebootOutput = os.popen("last reboot")
rebootLine = rebootOutput.readline()[:-1]
timePerDayDict = {}
dateFormat = "%b %d"
timeFormat = "%H:%M"

current_year = datetime.now().year
while rebootLine:
    reboot = rebootLine.split()
    reboot_date = " ".join(reboot[5:7])
    reboot_date = reboot_date[:4] + reboot_date[4:].zfill(2)
    if reboot_date not in timePerDayDict and len(timePerDayDict) == daysToShow:
        break
    if len(reboot) < 3:
        break
    if reboot[-1] == "running":
        reboot_time = datetime.strptime(
            f"{reboot[-3]} {reboot_date} {current_year}", "%H:%M %b %d %Y"
        )
        current_time = datetime.strptime(
            f"{datetime.strftime(datetime.now(), timeFormat)} {datetime.strftime(datetime.now(), dateFormat)} {current_year}",
            "%H:%M %b %d %Y",
        )
        timePerDayDict[reboot_date] = current_time - reboot_time
    else:
        reboot_duration = datetime.strptime(reboot[-1][1:-1], timeFormat)
        try:
            timePerDayDict[reboot_date] += timedelta(
                hours=reboot_duration.hour, minutes=reboot_duration.minute
            )
        except KeyError:
            timePerDayDict[reboot_date] = timedelta(
                hours=reboot_duration.hour, minutes=reboot_duration.minute
            )
    rebootLine = rebootOutput.readline()[:-1]

# handling idle times
try:
    with open(IDLETIME_FILE, "r") as file:
        idletimesDict = {}
        idletimes = file.read().split("\n")
        for idletime in idletimes:
            if idletime:
                idletime = idletime.split(" - ")
                idleDateStr = idletime[0].strip()
                if (
                    idleDateStr not in timePerDayDict
                    and len(timePerDayDict) == daysToShow
                ):
                    break
                idletimeObj = datetime.strptime(idletime[1], timeFormat)
                idletimeObj = timedelta(
                    hours=idletimeObj.hour, minutes=idletimeObj.minute
                )
                idletimesDict[idletime[0].strip()] = idletimeObj
except FileNotFoundError:
    print(colored(bold("No idletime file found"), "red"))
    idletimesDict = {}

# adjusting SECONDS_PER_BAR based on maxTime and MAX_BAR_LENGTH
maxTime = max(
    map(
        lambda day: timePerDayDict[day]
        - (
            timedelta(0)
            if args.with_idletimes
            else idletimesDict.get(day, timedelta(0))
        ),
        timePerDayDict,
    )
)
SECONDS_PER_BAR = maxTime.total_seconds() / MAX_BAR_LENGTH

# printing times
sumTime = timedelta(0)
for day in timePerDayDict:
    netTime = timePerDayDict[day] - (
        timedelta(0) if args.with_idletimes else idletimesDict.get(day, timedelta(0))
    )
    sumTime += netTime
    printTime(
        day,
        netTime,
        (
            idletimesDict.get(day, timedelta(0)).total_seconds()
            if args.with_idletimes
            else 0
        ),
    )

# printing total time
print(
    colored("Total (", COLOR_DATES)
    + colored(len(timePerDayDict), COLOR_TIMES)
    + colored(" days): ", COLOR_DATES)
    + bold(
        colored(
            f"{str(sumTime.days)+'d ' if sumTime.days else ''}{sumTime.seconds // 3600}h {sumTime.seconds // 60 % 60}m",
            "yellow",
        )
    )
    + (
        colored(" (including idle times): ", COLOR_DATES)
        if args.with_idletimes
        else colored(": ", COLOR_DATES)
    )
)
