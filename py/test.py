from files import Files
import json
import re

semesterFiles = Files("fall")
rawFile = semesterFiles.rawFile


class Test:
    def __init__(self):
        self.cl = dict()
        self.timeReg = r"[MTWRF]{1,5}\s+\d{4}-\d{4}"

    def sectionLine(self, row: str):
        return re.match(r"^\d{5}\s{2,}[A-Z]+\s{2,}\d{3}-\w{3}-\w{2}\s{2,}\
            (?:\w|\s|[\(\)<>&\+])+\s{2,}[MTWRF]{1,5}\s{2,}\d{4}-\d{4}", row)

    def lectureLine(self, row: str):
        return re.match(r"\s{25}Lecture\s{15}.+\s+[MTWRF]\
            {1,5}\s+\d{4}-\d{4}", row) or \
            re.match(r"\s{25}Lecture\s{15}.+", row)

    def brokenDisc(self, row: str):
        if re.search(r"(?<!\s)Lecture", row):
            return True

        if re.match(r"^\d{5}", row):
            if re.match(r"^\d{5}\s*\w+\d{3}-\w{3}-\w{2}", row):
                return True

        return False

    def doublelines(self, row: str):
        n = len(row) - len(row.lstrip())

        if n == 47 and not re.match(r".+\s{2,}", row):
            return True

        elif re.search(self.timeReg, row) and n == 47:
            return True

        return False

    def timeDuplicate(self, row: str):
        if re.match(r"^\d{5}", row):
            self.cl.clear()

            section, disc, code, * \
                title, day, time = [k.replace("\x00", "")
                                    for k in row.split(" ") if k != ""]

            self.cl["section"] = section
            self.cl["disc"] = disc
            self.cl["code"] = code
            self.cl["title"] = title
            self.cl[day] = time

            if code == "502-UNB-AB":
                pass

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


def main():
    raw: list[str] = []
    test = Test()

    with open(rawFile, "r") as file:
        raw = json.loads(file.read())

    for i, row in enumerate(raw):
        if any(f(row) for f in [
            test.brokenDisc,
            test.doublelines,
            test.timeDuplicate,
        ]):
            print(i, row, sep=": ")
        # if (re.search(r"[MTWRF]{1,5}\s+\d{4}-\d{4}", row)):
        #     print(i, row, sep=": ")


if __name__ == "__main__":
    main()
