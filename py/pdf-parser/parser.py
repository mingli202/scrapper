from files import Files
from test import Test

import re
import json
import os


class Scraper:
    def __init__(self, files: Files):
        self.files = files

    def run(self):
        self.writeToRaw()
        if not self.testRawFile():
            print("Tests failed")
            exit(1)
        self.scrape()

    def writeToRaw(self):
        if os.path.exists(self.files.rawFile):
            print("Raw file already exists")
            return

        with open(self.files.pdfName, "rb") as file:
            lines = file.read()

        arr = lines.decode("UTF-16").split("\n")

        arr: list[str] = [
            line
            for line in arr
            if line.find("SCHEDULE OF CLASSES - FALL 2024") == -1
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

    def scrape(self):
        cl = Section()
        sections = []
        programs = ["Courses", "Arts, Literature & Communication"]


class Section:
    def __init__(self):
        self.cl = {
            "program": "",
            "course": "",
            "code": "",
            "section": "",
            "lecture": {},
            "lab": {},
            "more": "",
        }
