import json
import os
import re
from typing import Callable
from models import Section
import inspect


from files import Files
import unittest


class Parser:
    parse_improvement = False

    def __init__(self, files: Files):
        self.files = files

        self.sections: list[dict] = []
        self.currentClass = Section()

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

    def updateSection(self, section: Section):
        if section.section != "":
            self.sections.append(section.model_dump())

            section.code = ""
            section.section = ""
            section.lecture = {}
            section.lab = {}
            section.more = ""
            section.count += 1

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

        for row in raw:
            space = len(row) - len(row.lstrip())
            text = row.strip()
            a = [k for k in row.split(" ") if k != ""]

            if self.parse_improvement:
                if self.parse_program_line(text, space):
                    pass
                elif self.parse_course_line(text, space):
                    pass
                elif self.parse_code_header(space):
                    continue
                elif self.parse_section_line(row, a):
                    pass
                elif self.parse_lecture_line(text, a):
                    pass
                elif self.parse_lab_line(space, a):
                    pass
                elif self.parse_laboratory_line(text, a):
                    pass
                elif self.parse_random_floating_line(text):
                    pass
                elif self.parse_course_line(text, space):
                    pass
                else:
                    print("no match", text)
                    exit()

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

    def parse_program_line(self, text: str, space: int) -> bool:
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
        ]

        if not (any(text.find(x) != -1 for x in programs) and space >= 30):
            return False

        if text != cl.program:
            self.updateSection(cl)
            cl.course = ""

        cl.program = text
        return True

    def parse_course_line(self, text: str, space: int) -> bool:
        cl = self.currentClass

        if not (text.isupper() and space == 0):
            return False

        if text != cl.course:
            self.updateSection(cl)

        cl.course = text
        return True

    def parse_code_header(self, space: int) -> bool:
        return space == 1

    def parse_section_line(self, row: str, a: list[str]) -> bool:
        cl = self.currentClass

        if not re.match(r"^\d{5}", row):
            return False

        self.updateSection(cl)

        section, _, code, *title, day, time = a
        cl.section = section
        cl.code = code
        cl.lecture["title"] = " ".join(title)
        cl.lecture[day] = time

        return True

    def parse_lecture_line(self, text: str, a: list[str]) -> bool:
        cl = self.currentClass

        if not re.match("^Lecture", text):
            return False

        if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
            _, *prof, day, time = a
            cl.lecture[day] = time
        else:
            _, *prof = a

        cl.lecture["prof"] = " ".join(prof)

        return True

    def parse_lab_line(self, space: int, a: list[str]) -> bool:
        cl = self.currentClass

        if not space == 13:
            return False

        _, code, *title, day, time = a
        cl.code = code
        cl.lab["title"] = " ".join(title)
        cl.lab[day] = time

        return True

    def parse_laboratory_line(self, text: str, a: list[str]) -> bool:
        cl = self.currentClass

        if not re.match("^Laboratory", text):
            return False

        if re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", text):
            _, *prof, day, time = a
            cl.lab[day] = time
        else:
            _, *prof = a

        cl.lab["prof"] = " ".join(prof)

        return True

    def parse_random_floating_line(self, text: str) -> bool:
        cl = self.currentClass

        if m := re.search(r"([MTWRF]{1,5})\s+(\d{4}-\d{4})", text):
            if cl.lab:
                cl.lab[m.group(1)] = m.group(2)
            else:
                cl.lecture[m.group(1)] = m.group(2)

            return True

        return False

    def parse_more_line(self, text: str, space: int) -> bool:
        cl = self.currentClass

        if space not in [25, 26]:
            return False

        if re.match("^ADDITIONAL", text):
            cl.more += f"{text}\n"
        else:
            cl.more += f"{text} "

        return True


class TestParse(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files = Files()
        cls.parser = Parser(cls.files)

    def setUp(self) -> None:
        self.parser.sections = []
        self.parser.currentClass = Section()

    def get_row_data(self, row: str) -> tuple[int, str, list[str]]:
        space = len(row) - len(row.lstrip())
        text = row.strip()
        a = [k for k in row.split(" ") if k != ""]

        return space, text, a

    def t(self, func: Callable) -> Callable:
        sig = inspect.signature(func)

        def f(row: str):
            space, text, a = self.get_row_data(row)
            variable_dict = {"space": space, "text": text, "a": a, "row": row}
            function_params = {k: variable_dict[k] for k in sig.parameters.keys()}
            func(**function_params)

        return f

    def test_program_line(self):
        t = self.t(self.parser.parse_program_line)

        for s in [
            "                                                    Science Courses",
            "                                      Social Science / Commerce Courses",
            "                                                  Visual Arts Courses",
            "                                                      Arts & Science",
            "                                        Arts, Literature & Communication",
            "                                                 Liberal Arts Courses",
            "                                                   Pathways Courses",
            "                                                           English",
            "                                                           French",
            "                                                        Humanities",
            "                                                  Physical Education",
            "                                              Complementary Courses",
        ]:
            t(s)
            self.assertEqual(self.parser.currentClass, Section(program=s.strip()))

        t("this should not work")
        self.assertEqual(
            self.parser.currentClass, Section(program="Complementary Courses")
        )

    def test_course_line(self):
        t = self.t(self.parser.parse_course_line)

        t("ENGLISH")
        self.assertEqual(
            self.parser.currentClass, Section(course="ENGLISH"), "should set"
        )

        t("HUMANITIES                      ")
        self.assertEqual(
            self.parser.currentClass, Section(course="HUMANITIES"), "should replace"
        )

        t("asdfoweur023984")
        self.assertEqual(
            self.parser.currentClass, Section(course="HUMANITIES"), "should not work"
        )

        t("  FRENCH")
        self.assertEqual(
            self.parser.currentClass, Section(course="HUMANITIES"), "should not work"
        )

    def test_section_line(self):
        t = self.t(self.parser.parse_section_line)

        self.assertEqual(
            self.parser.currentClass,
            Section(course="", section="", code="", lecture={}),
        )

        t(
            "00001        HISA        520-AH3-AB            Art History III - Understanding Contemporary Art        W              1300-1600"
        )
        self.assertEqual(
            self.parser.currentClass,
            Section(
                course="",
                section="00001",
                code="520-AH3-AB",
                lecture={
                    "title": "Art History III - Understanding Contemporary Art",
                    "W": "1300-1600",
                },
            ),
            "should have these values",
        )

        t(
            "00001        CRIMINOLOGY    310-518-AB            Fieldwork I - Practical                                 MW             0830-1800"
        )
        self.assertEqual(
            self.parser.currentClass,
            Section(
                count=1,
                course="",
                section="00001",
                code="310-518-AB",
                lecture={
                    "title": "Fieldwork I - Practical",
                    "MW": "0830-1800",
                },
            ),
            "should replace with these new values",
        )

        self.assertEqual(self.parser.sections.__len__(), 1)

    def test_lecture_line(self):
        t = self.t(self.parser.parse_lecture_line)

        t("                         Laboratory            MacLean, Roger")
        self.assertEqual(self.parser.currentClass, Section())

        t("                         Lecture")
        self.assertEqual(self.parser.currentClass, Section(lecture={"prof": ""}))

        t("                         Lecture               Dukanic, Filip")
        self.assertEqual(
            self.parser.currentClass, Section(lecture={"prof": "Dukanic, Filip"})
        )

        t(
            "                         Lecture               Lucier, Jason                                           W              1330-1430"
        )
        self.assertEqual(
            self.parser.currentClass,
            Section(lecture={"prof": "Lucier, Jason", "W": "1330-1430"}),
        )

    def test_lab_line(self):
        t = self.t(self.parser.parse_lab_line)

        t(
            "             DENT        111-316-AB            Periodontal Instrumentation                             R             0830-1030"
        )
        self.assertEqual(
            self.parser.currentClass,
            Section(
                code="111-316-AB",
                lab={"title": "Periodontal Instrumentation", "R": "0830-1030"},
            ),
        )

    def test_laboratory_line(self):
        t = self.t(self.parser.parse_laboratory_line)

        t("                         Laboratory")
        self.assertEqual(self.parser.currentClass, Section(lab={"prof": ""}))

        t("                         Laboratory            MacLean, Roger")
        self.assertEqual(
            self.parser.currentClass, Section(lab={"prof": "MacLean, Roger"})
        )

        t(
            "                         Laboratory            Hasko, Anila                                            F              1030-1230"
        )
        self.assertEqual(
            self.parser.currentClass,
            Section(lab={"prof": "Hasko, Anila", "F": "1030-1230"}),
        )

    def test_random_floating_time(self):
        t = self.t(self.parser.parse_random_floating_line)

        t(
            "                                                                                                       R              1600-1800"
        )
        self.assertEqual(self.parser.currentClass, Section(lecture={"R": "1600-1800"}))


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

no_teacher_case = [
    "00002        BIOL        101-1P1-AB            Introduction to Biology                                 W              1300-1500",
    "                         Lecture",
    "                         *** Not open, may open during registration ***",
    "             BIOL        101-1P1-AB            Introduction to Biology                                 R              1200-1400",
    "                         Laboratory",
]

if __name__ == "__main__":
    unittest.main()
