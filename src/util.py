import json
from pydantic_core import from_json
from files import Files
from models import Rating, Section
import math


def stripAccent(s: str):
    s = s.replace("\u00e9", "e")  # * removes é
    s = s.replace("\u00e8", "e")  # * removes è
    s = s.replace("\u00e2", "a")  # * removes â
    s = s.replace("\u00e7", "c")  # * removes ç
    s = s.replace("\u00e0", "a")  # * removes à
    s = s.replace("\u0000", "")  # * removes null character

    return s


def addRating(files: Files):
    sections: list[Section] = []
    ratings: list[Rating] = []

    with open(files.outFile) as file:
        sections = [Section(**s) for s in from_json(file.read())]

    with open(files.ratings) as file:
        ratings = [Rating(**r) for r in from_json(file.read())]

    ratings_dict: dict[str, Rating] = {}
    for rating in ratings:
        ratings_dict[rating.prof] = rating

    sections_with_rating = []

    for section in sections:
        s = section.model_dump()

        r = ratings_dict.get(s["lecture"]["prof"])
        if r is None:
            r = {}
        else:
            r = r.model_dump()

        s["lecture"]["rating"] = r

        if "prof" in s["lab"]:
            r = ratings_dict.get(s["lab"]["prof"])
            if r is None:
                r = {}
            else:
                r = r.model_dump()

            s["lab"]["rating"] = r

        sections_with_rating.append(s)

    with open(files.classesFile, "w") as file:
        file.write(json.dumps(sections_with_rating, indent=2))


def handleViewData(targetClass: dict):
    c = dict(targetClass)

    col = ["M", "T", "W", "R", "F"]
    row = []

    for i in range(21):
        if i % 2 == 0:
            row.append(i * 50 + 800)
        else:
            row.append(math.floor(i / 2) * 2 * 50 + 830)

    lecture: dict[str, str] = dict(c["lecture"])
    lecture.pop("title", False)
    lecture.pop("prof", False)
    lecture.pop("rating", False)

    lab: dict[str, str] = dict(c["lab"])
    lab.pop("title", False)
    lab.pop("prof", False)
    lab.pop("rating", False)

    days = lecture | lab

    viewData = []

    for i in days:
        t = days[i]
        t = t.split("-")

        try:
            rowStart = row.index(int(t[0])) + 1
        except ValueError:
            rowStart = 1

        try:
            rowEnd = row.index(int(t[1])) + 1
        except ValueError:
            rowEnd = 21

        for d in i:
            if d == "S":
                continue

            colStart = col.index(d) + 1

            viewData.append({colStart: [rowStart, rowEnd]})

    c["viewData"] = viewData
    return c


def addViewData(files: Files):
    classes: list[dict] = []
    with open(files.classesFile, "r") as file:
        classes = from_json(file.read())

    polished = {}
    for index, course in enumerate(classes):
        polished.update({index: handleViewData(course)})

    with open(files.classesFile, "w") as file:
        file.write(json.dumps(polished, indent=2))
