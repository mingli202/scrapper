import json
import os
import re
from models import Section


from files import Files

from .test import Test


class Parser:
    def __init__(self, files: Files):
        self.files = files

    def run(self):
        self.writeToRaw()
        if not self.testRawFile():
            print("Tests failed")
            exit(1)
        self.parse()

    def writeToRaw(self):
        if os.path.exists(self.files.rawFile):
            print("Raw file already exists")
            return

        with open(self.files.pdfName, "rb") as file:
            lines = file.read()

        arr = lines.decode("UTF-16").split("\n")

        arr: list[str] = [
            line.replace("\u0000", "")
            for line in arr
            # TODO: Change for next semester
            if line.find("SCHEDULE OF CLASSES - WINTER 2025") == -1
            and len(line) != 0
            and not re.match(r"^SECTION", line)
            and not re.match(r"^John Abbott", line)
        ]

        with open(self.files.rawFile, "w") as file:
            file.write(json.dumps(arr, indent=2))

    def testRawFile(self):
        raw: list[str] = []
        test = Test()

        with open(self.files.rawFile, "r") as file:
            raw = json.loads(file.read())

        p = True
        for i, row in enumerate(raw):
            if any(
                f(row)
                for f in [
                    test.brokenDisc,
                    test.doublelines,
                    test.timeDuplicate,
                ]
            ):
                print(i, row, sep=": ")
                p = False

        return p

    def parse(self):
        if os.path.exists(self.files.outFile):
            print("out_file already exists")
            return

        def updateSection(section: Section, sections: list[dict]):
            if section.section != "":
                sections.append(section.model_dump())

                section.code = ""
                section.section = ""
                section.lecture = {}
                section.lab = {}
                section.more = ""
                section.count += 1

        cl = Section()
        sections: list[dict] = []
        programs = [
            "Courses",
            "Arts, Literature & Communication",
            "Arts & Science",
            "English",
            "French",
            "Humanities",
            "Physical Education",
            "English",
        ]

        raw: list[str] = []

        with open(self.files.rawFile, "r") as file:
            raw = json.loads(file.read())

        for i, row in enumerate(raw):
            print(i)

            space = len(row) - len(row.lstrip())
            text = row.strip()
            a = [k for k in row.split(" ") if k != ""]

            # program line
            if any(text.find(x) != -1 for x in programs) and space >= 30:
                if text != cl.program:
                    updateSection(cl, sections)
                    cl.course = ""

                cl.program = text

            # course line
            elif text.isupper() and space == 0:
                if text != cl.course:
                    updateSection(cl, sections)

                cl.course = text

            # code header
            elif space == 1:
                continue

            # section line
            elif re.match(r"^\d{5}", row):
                updateSection(cl, sections)

                section, _, code, *title, day, time = a
                cl.section = section
                cl.code = code
                cl.lecture["title"] = " ".join(title)
                cl.lecture[day] = time

            # lecture line
            elif re.match("^Lecture", text):
                if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
                    _, *prof, day, time = a
                    cl.lecture[day] = time
                else:
                    _, *prof = a

                cl.lecture["prof"] = " ".join(prof)

            # lab line
            elif space == 13:
                _, code, *title, day, time = a
                cl.code = code
                cl.lab["title"] = " ".join(title)
                cl.lab[day] = time

            elif re.match("^Laboratory", text):
                if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
                    _, *prof, day, time = a
                    cl.lab[day] = time
                else:
                    _, *prof = a

                cl.lab["prof"] = " ".join(prof)

            # random floating time
            elif m := re.search(r"([MTWRF]{1,5})\s+(\d{4}-\d{4})", text):
                if cl.lab:
                    cl.lab[m.group(1)] = m.group(2)
                else:
                    cl.lecture[m.group(1)] = m.group(2)

            # more
            elif space in [25, 26]:
                if re.match("^ADDITIONAL", text):
                    cl.more += f"{text}\n"
                else:
                    cl.more += f"{text} "

            else:
                print("no match", text)
                exit()

        updateSection(cl, sections)

        with open(self.files.outFile, "w") as file:
            file.write(json.dumps(sections, indent=2))
