import json
import re
from files import Files
import os


semesterFiles = Files()
pdfName = semesterFiles.pdfName
rawFile = semesterFiles.rawFile
outFile = semesterFiles.outFile
organized = semesterFiles.organized

programs = ["Courses", "Arts, Literature & Communication"]
sectionReg = r"^\d{5}\s{2,}[A-Z]+\s{2,}\d{3}-\w{3}-\w{2}\s{2,}(?:\w|\s|[\(\)<>&\+])+\s{2,}[MTWRF]{1,5}\s{2,}\d{4}-\d{4}$"


class Class:
    def __init__(self):
        self.cl = {
            "program": "",
            "course": "",
            "code": "",
            "section": "",
            "disc": "",
            "lecture": {},
            "lab": {},
            "more": ""
        }


def readRawArray():
    with open(rawFile, "r") as file:
        raw = json.loads(file.read())

    cl = Class()
    sections = []

    for i, row in enumerate(raw):
        sectionLine = re.match(sectionReg, row)

        if sectionLine:
            print(i, row, sep=": ")


def writeToA():
    if os.path.exists(rawFile):
        return

    with open(pdfName, "rb") as file:
        lines = file.read()

    a = lines.decode("UTF-16")
    b = a.split("\n")

    def fn(s: str):
        if (
            s.strip() == ""
            or s.strip() == "SCHEDULE OF CLASSES - FALL 2024"
            or re.match("^John Abbott College", s)
            or re.match("^SECTION", s)
        ):
            return False
        return True

    raw = list(filter(fn, b))

    with open(rawFile, "w") as file:
        file.write(json.dumps(raw, indent=2))


def writeToOut():
    with open(rawFile, "r") as file:
        raw = json.loads(file.read())

    program = ""
    course = ""
    codeHeader = ""
    code = ""
    section = ""
    more = ""
    disc = ""
    lecture = {}
    lab = {}

    time = ""
    day = ""

    Sections = []

    codeHeader2nLine = False

    sectionFormat = "[0-9][0-9][0-9][0-9][0-9]"

    timeFormat = "[0-9][0-9][0-9][0-9]-[0-9][0-9][0-9][0-9]"

    def handleSectionChange(
        section, disc, lecture, lab, more, code, program, course, codeHeader, count
    ):
        Sections.append(
            {
                "count": count,
                "program": program,
                "course": course,
                "code": code,
                "codeHeader": codeHeader,
                "section": section,
                "disc": disc,
                "lecture": lecture,
                "lab": lab,
                "more": more,
            }
        )

    count = 0

    for index, i in enumerate(raw):
        print(index)

        space = len(i) - len(i.lstrip())
        text = i.strip().replace("\u0000", "")
        a = list(filter(lambda i: i != "", i.split(" ")))

        # program
        if space >= 30 and not any([re.match(timeFormat, j) for j in a]):
            if text != program:
                handleSectionChange(
                    section,
                    disc,
                    lecture,
                    lab,
                    more,
                    code,
                    program,
                    course,
                    codeHeader,
                    count,
                )
                section = ""
                disc = ""
                lecture = {}
                lab = {}
                more = ""
                code = ""
                count += 1
                course = ""

            program = text

        # section line
        elif re.match(sectionFormat, text):
            if text != a[0]:
                handleSectionChange(
                    section,
                    disc,
                    lecture,
                    lab,
                    more,
                    code,
                    program,
                    course,
                    codeHeader,
                    count,
                )
                section = ""
                disc = ""
                lecture = {}
                lab = {}
                more = ""
                code = ""
                count += 1

            section, disc, code, *title, day, time = a
            lecture = {"title": " ".join(title), day.replace(
                "\u0000", ""): time.replace("\u0000", "")}

        # course
        elif text.isupper() and space == 0:
            if course != text:
                handleSectionChange(
                    section,
                    disc,
                    lecture,
                    lab,
                    more,
                    code,
                    program,
                    course,
                    codeHeader,
                    count,
                )
                section = ""
                disc = ""
                lecture = {}
                lab = {}
                more = ""
                code = ""
                count += 1

            course = text

        # codeHeader
        if space == 1:
            if codeHeader2nLine:
                codeHeader += f"\n{text}"
            else:
                if text not in codeHeader:
                    handleSectionChange(
                        section,
                        disc,
                        lecture,
                        lab,
                        more,
                        code,
                        program,
                        course,
                        codeHeader,
                        count,
                    )
                    section = ""
                    disc = ""
                    lecture = {}
                    lab = {}
                    more = ""
                    code = ""
                    count += 1

                codeHeader = text

            codeHeader2nLine = True
        else:
            codeHeader2nLine = False

        # lect line
        if re.match("^Lecture", text):
            if any([re.match(timeFormat, j) for j in a]):
                l, *prof, day, time = a

            else:
                l, *prof = a

            lecture.update({"prof": " ".join(prof), day.replace(
                "\u0000", ""): time.replace("\u0000", "")})

        # lab line
        elif space == 13:
            disc, code, *title, day, time = a
            lab = {"title": " ".join(title), day.replace(
                "\u0000", ""): time.replace("\u0000", "")}

        # lab
        elif re.match("^Laboratory", text):
            l, *prof = a
            lab.update({"prof": " ".join(prof)})

        else:
            if any([re.match(timeFormat, j) for j in a]):
                *l, day, time = a
                lecture.update({day.replace("\u0000", ""): time.replace("\u0000", "")})
            elif space in [25, 26]:
                if re.match("^ADDITIONAL", text):
                    more += f"{text}\n"
                else:
                    more += f"{text} "

    handleSectionChange(
        section, disc, lecture, lab, more, code, program, course, codeHeader, count
    )

    def cond(obj):
        if obj["section"] == "":
            return False
        return True

    filtered = list(filter(cond, Sections))

    with open(outFile, "w") as file:
        file.write(json.dumps(filtered, indent=2))

    # organized
    data = {}

    for i in filtered:
        if i["program"] not in data:
            data[i["program"]] = {}

        if i["course"] not in data[i["program"]]:
            data[i["program"]][i["course"]] = {}

        if i["code"] not in data[i["program"]][i["course"]]:
            data[i["program"]][i["course"]][i["code"]] = {}

        data[i["program"]][i["course"]][i["code"]][i["section"]] = {
            "disc": i["disc"],
            "lecture": i["lecture"],
            "lab": i["lab"],
            "more": i["more"],
        }

    with open(organized, "w") as file:
        file.write(json.dumps(data, indent=2))


if __name__ == "__main__":
    writeToA()
    writeToOut()
    # readRawArray()
    # pass
