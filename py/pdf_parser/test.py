import re


class Test:
    def __init__(self):
        self.cl = {}

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
