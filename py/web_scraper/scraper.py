import json
import os
import re
from concurrent.futures import Future, ThreadPoolExecutor

import requests
from files import Files
from models import Rating, Section
from pydantic_core import from_json

import util


class Scraper:
    def __init__(self, files: Files):
        self.files = files

    def run(self):
        professors = self.get_professors()

        ratings: list[Rating] = []

        def fn(prof: str):
            rating = self.get_rating(prof)
            print(rating)
            ratings.append(rating)

        with ThreadPoolExecutor(max_workers=10) as e:
            for prof in professors:
                e.submit(fn, prof)

        with open(self.files.ratings, "w") as file:
            file.write(json.dumps([r.model_dump() for r in ratings], indent=2))

    def get_professors(self) -> list[str]:
        if not os.path.exists(self.files.professors):
            profs: set[str] = set()
            with open(self.files.outFile, "r") as file:
                classes: list[Section] = [Section(**d) for d in from_json(file.read())]

                for cl in classes:
                    print(cl.count)
                    lecture_prof = cl.lecture.get("prof")
                    lab_prof = cl.lecture.get("prof")

                    if lecture_prof:
                        profs.add(lecture_prof)

                    if lab_prof:
                        profs.add(lab_prof)

            with open(self.files.professors, "w") as file:
                file.write(json.dumps(list(profs)))

        professors: list[str] = []
        with open(self.files.professors, "r") as file:
            professors = from_json(file.read())

        return professors

    def get_rating(self, prof: str) -> Rating:
        rating = Rating(prof=prof)
        _prof = util.stripAccent(prof).lower()

        fname = _prof.split(", ")[1]
        lname = _prof.split(", ")[0]

        pids = self.get_pids(lname)
        if len(pids) == 0:
            return rating

        max = 0
        id = pids[0][0]
        if len(pids) > 1:
            for pid in pids:
                c = self.closelness(pid[1].lower(), fname)
                if c > max and c > 0.5:
                    id = pid[0]
                    max = c

        if _r := self.get_stats_from_pid(id, prof):
            rating = _r

        return rating

    def closelness(self, candidate: str, target: str) -> float:
        i = 0
        for char in target:
            if char == candidate[i]:
                i += 1
                if i == len(candidate):
                    break

        return i / len(target)

    def get_pids(self, lastname: str) -> list[tuple[str, str]]:
        url = f"https://www.ratemyprofessors.com/search/professors/12050?q={lastname}"
        r = requests.get(url)

        if r.status_code != 200:
            raise

        return re.findall(
            r'{"__id":"\w+","__typename":"Teacher","id":"\w+","legacyId":(\d+),"avgRating":[\d\.]+,"numRatings":[\d\.]+,"wouldTakeAgainPercent":[\d\.]+,"avgDifficulty":[\d\.]+,"department":"[\w ]+","school":{"__ref":"U2Nob29sLTEyMDUw"},"firstName":"([\w\' -]+)","lastName":'
            + f'"{lastname}"'
            + r',"isSaved":false}',
            r.text,
            re.I,
        )

    def get_stats_from_pid(self, pid: str, prof: str) -> Rating | None:
        SCHOOL_ID = 12050
        SCHOOL_REF = "U2Nob29sLTEyMDUw"

        url = f"https://www.ratemyprofessors.com/ShowRatings.jsp?tid={pid}"
        r = requests.get(url)

        if r.status_code != 200:
            print("Error")
            raise

        if matches := re.search(
            rf'"__typename":"Teacher".+"legacyId":{pid}'
            + r',"firstName":"[\w\' -]+","lastName":"[\w\' -]+","department":"[\w ]+","school":{"__ref":"'
            + f"{SCHOOL_REF}"
            + r'"}.+"numRatings":([\d\.]+).+"avgRating":([\d\.]+).+"avgDifficulty":([\d\.]+),"wouldTakeAgainPercent":([\d\.]+).+'
            + rf'"__typename":"School","legacyId":{SCHOOL_ID}',
            r.text,
        ):
            (
                numRating,
                avgRating,
                difficulty,
                takeAgain,
            ) = matches.groups()

            try:
                rating = Rating(
                    prof=prof,
                    nRating=round(float(numRating)),
                    avg=round(float(avgRating), 1),
                    takeAgain=round(float((takeAgain))),
                    difficulty=round(float(difficulty), 1),
                    status="found",
                )

                rating.score = round(
                    (((rating.avg * rating.nRating) + 5) / (rating.nRating + 2))
                    * 100
                    / 5,
                    1,
                )

                return rating
            except ValueError:
                return None

        return None