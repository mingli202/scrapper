import re
import unittest

from pydantic_core import from_json

from files import Files


class ParserTest(unittest.TestCase):
    def setUp(self):
        self.cl = {}
        self.files = Files()

    def test_brokenDisc(self):
        raw: list[str] = []
        with open(self.files.rawFile, "r") as file:
            raw = from_json(file.read())

        is_valid = True
        for i, row in enumerate(raw):
            if self.brokenDisc(row):
                print(i, row, sep=": ")
                is_valid = False

        if not is_valid:
            raise

    def test_time_doublelines(self):
        raw: list[str] = []
        with open(self.files.rawFile, "r") as file:
            raw = from_json(file.read())

        is_valid = True
        for i, row in enumerate(raw):
            if self.doublelines(row):
                print(i, row, sep=": ")
                is_valid = False

        if not is_valid:
            raise

    def test_time_duplicate(self):
        raw: list[str] = []
        with open(self.files.rawFile, "r") as file:
            raw = from_json(file.read())

        is_valid = True
        for i, row in enumerate(raw):
            if self.timeDuplicate(row):
                print(i, row, sep=": ")
                is_valid = False

        if not is_valid:
            raise

    def brokenDisc(self, row: str):
        if re.search(r"(?<!\s)Lecture", row):
            return True

        if re.match(r"^\d{5}", row):
            if re.match(r"^\d{5}\s*\w+\d{3}-\w{3}-\w{2}", row):
                return True

        return False

    def doublelines(self, row: str):
        n = len(row) - len(row.lstrip())

        if n == 47:
            return True

        return False

    def timeDuplicate(self, row: str):
        if re.match(r"^\d{5}", row):
            self.cl = {}

            section, disc, code, *title, day, time = [
                k.replace("\x00", "") for k in row.split(" ") if k != ""
            ]

            self.cl["section"] = section
            self.cl["disc"] = disc
            self.cl["code"] = code
            self.cl["title"] = title
            self.cl[day] = time

        else:
            dayTime = re.search(r"([MTWRF])\s*(\d{4}-\d{4})", row)
            if dayTime:
                day = dayTime.group(1)
                time = dayTime.group(2)

                if day in self.cl:
                    return True
                else:
                    self.cl[day] = time

        return False


if __name__ == "__main__":
    unittest.main()
