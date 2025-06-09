import json
import os
import re
from models import Section, LecLab, Time


from files import Files
import unittest


class Parser:
    def __init__(self, files: Files):
        self.files = files

        self.sections: list[dict] = []
        self.currentClass = Section()
        self.tmp = {}

    def run(self):
        self.writeToRaw()

        if not unittest.main(
            module="pdf_parser.raw_file_test", exit=False
        ).result.wasSuccessful():
            print("parser test unsuccessful")
            exit(1)

        self.parse()

        if not unittest.main(
            module="pdf_parser.out_file_test", exit=False
        ).result.wasSuccessful():
            print("parser test unsuccessful")
            exit(1)

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
            if line.find("SCHEDULE OF CLASSES - FALL 2025") == -1
            and len(line) != 0
            and not re.match(r"^SECTION", line)
            and not re.match(r"^John Abbott", line)
        ]

        with open(self.files.rawFile, "w") as file:
            file.write(json.dumps(arr, indent=2))

    def updateSection(self, tmp: LecLab):
        section = self.currentClass

        if section.section == "":
            return

        if section.lab:
            section.lab.update(tmp)
        else:
            if not section.lecture:
                section.lecture = LecLab()

            section.lecture.update(tmp)

        self.sections.append(section.model_dump())

        section.code = ""
        section.section = ""
        section.lecture = None
        section.lab = None
        section.more = ""
        section.count += 1

        tmp.title = ""
        tmp.prof = ""
        tmp.time = Time()

    def parse(self):
        if os.path.exists(self.files.outFile):
            print("out_file already exists")
            return

        raw: list[str] = []

        with open(self.files.rawFile, "r") as file:
            raw = json.loads(file.read())

        tmp = LecLab()

        for row in raw:
            self.parse_row(row, tmp)

        self.updateSection(tmp)

        with open(self.files.outFile, "w") as file:
            file.write(json.dumps(self.sections, indent=2))

    def parse_row(self, row: str, tmp):
        space = len(row) - len(row.lstrip())
        text = row.strip()
        a = [k for k in row.split(" ") if k != ""]

        if self.parse_program_line(text, space, tmp):
            pass
        elif self.parse_course_line(text, space, tmp):
            pass
        elif self.parse_code_header(space):
            pass
        elif self.parse_section_line(row, a, tmp):
            pass
        elif self.parse_lecture_line(text, a, tmp):
            pass
        elif self.parse_lab_line(space, a, tmp):
            pass
        elif self.parse_laboratory_line(text, a, tmp):
            pass
        elif self.parse_random_floating_line(text, tmp):
            pass
        elif self.parse_more_line(text, space):
            pass
        else:
            print("no match", text)
            exit()

    def parse_program_line(self, text: str, space: int, tmp: LecLab) -> bool:
        cl = self.currentClass

        programs = [
            "Courses",
            "Arts, Literature & Communication",
            "Arts & Science",
            "English",
            "French",
            "Humanities",
            "Physical Education",
            "English",
            "Career Programs",
        ]

        if not (any(text.find(x) != -1 for x in programs) and space >= 30):
            return False

        if text != cl.program:
            self.updateSection(tmp)
            cl.course = ""

        cl.program = text
        return True

    def parse_course_line(self, text: str, space: int, tmp: LecLab) -> bool:
        cl = self.currentClass

        if not (text.isupper() and space == 0):
            return False

        if text != cl.course:
            self.updateSection(tmp)

        cl.course = text
        return True

    def parse_code_header(self, space: int) -> bool:
        return space == 1

    def parse_section_line(self, row: str, a: list[str], tmp: LecLab) -> bool:
        if not re.match(r"^\d{5}", row):
            return False

        cl = self.currentClass
        self.updateSection(tmp)

        section, _, code, *title, day, time = a
        cl.section = section
        cl.code = code

        tmp.title = " ".join(title)
        tmp.update_time({day: [time]})

        return True

    def parse_lecture_line(self, text: str, a: list[str], tmp: LecLab) -> bool:
        cl = self.currentClass

        if not re.match("^Lecture", text):
            return False

        if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
            _, *prof, day, time = a

            tmp.time.setdefault(day, []).append(time)
        else:
            _, *prof = a

        tmp.prof = " ".join(prof)

        if not cl.lecture:
            cl.lecture = LecLab()
        cl.lecture.update(tmp)

        tmp.clear()

        return True

    def parse_lab_line(self, space: int, a: list[str], tmp: LecLab) -> bool:
        cl = self.currentClass

        if not space == 13:
            return False

        _, code, *title, day, time = a
        cl.code = code
        tmp.title = " ".join(title)
        tmp.update_time({day: [time]})

        return True

    def parse_laboratory_line(self, text: str, a: list[str], tmp: LecLab) -> bool:
        cl = self.currentClass

        if not re.match("^Laboratory", text):
            return False

        if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
            _, *prof, day, time = a
            tmp.update_time({day: [time]})
        else:
            _, *prof = a

        tmp.prof = " ".join(prof)

        if not cl.lab:
            cl.lab = LecLab()
        cl.lab.update(tmp)

        tmp.clear()

        return True

    def parse_random_floating_line(self, text: str, tmp: LecLab) -> bool:
        if m := re.search(r"([MTWRF]{1,5})\s+(\d{4}-\d{4})", text):
            tmp.update_time({m.group(1): [m.group(2)]})

            return True

        return False

    def parse_more_line(self, text: str, space: int) -> bool:
        cl = self.currentClass

        if space not in [25, 26]:
            return False

        if re.match("^ADDITIONAL", text) or re.match(r"\*\*\*.*\*\*\*", text):
            cl.more += f"{text}\n"
        else:
            cl.more += f"{text} "

        return True


section_edge_case = [
    "00001        THEA        561-A5R-AB            Production Lab 3                                        M             1430-1730",
    "                         Lecture               Fauquembergue, Kevin                                    W             1100-1200",
    "                         ADDITIONAL FEE:       $60.00                                                  W             1800-2000",
    "                                                                                                       F              1430-1830",
]

blended_section_case = [
    "00001        INFO        393-JEB-AB            Information Sources & Services III (Blended)            TR             1330-1530",
    "                         Lecture               Maude, Melissa",
    "                         BLENDED LEARNING. This course will be delivered in blended learning format, involving a percentage of ",
    "                         technology-mediated asynchronous lectures, labs and/or other activities and a percentage in person on ",
    "                         campus lectures. A computer, reliable internet connection, webcam, and microphone are required to ",
    "                         complete your asynchronous activities.",
]
