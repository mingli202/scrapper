import os
import unittest

from pydantic_core import from_json
from files import Files

from models import Rating
from web_scraper.scraper import Scraper
import json


class ScraperTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.files = Files()
        cls.professors: list[str] = []
        with open(cls.files.professors, "r") as file:
            cls.professors = from_json(file.read())
        cls.scraper = Scraper(cls.files)

    def test_prof_rating_regex(self):
        self.assertIsNotNone(self.scraper.get_stats_from_pid("817818", "Grant, Grell"))

    def test_unique_lastname(self):
        professors: list[str] = []
        with open(self.files.professors, "r") as file:
            professors = from_json(file.read())

        not_unique_last_name: set[str] = set()

        lastnames: set[str] = set()
        for prof in professors:
            lname, _ = prof.split(", ")
            if lname != "TBA-1" and lname in lastnames:
                not_unique_last_name.add(prof)

            else:
                lastnames.add(lname)

        if not_unique_last_name.__len__() > 0:
            print(not_unique_last_name)

    def test_closelness(self):
        c = self.scraper.closeness("Grgoy", "Gregory")
        self.assertEqual(c, 5 / 7)

        c = self.scraper.closeness("Greg", "Gregory")
        self.assertEqual(c, 4 / 7)

    def test_valid_pids(self):
        pids = self.scraper.get_pids("wang")
        self.assertEqual(len(pids), 1)

    def test_duplicate_pids(self):
        pids = self.scraper.get_pids("Provencher")
        self.assertEqual(len(pids), 2)  # there are 2 provencher

    def test_no_pids(self):
        pids = self.scraper.get_pids("Klochko")
        self.assertEqual(len(pids), 0)  # reseults are N/A

    def test_department_with_space_and_duplicate_pids(self):
        pids = self.scraper.get_pids("young")
        self.assertEqual(len(pids), 2)  # department had a space

    def test_missing_rating(self):
        rating, _ = self.scraper.get_rating(
            "Voinea, Sorin", self.scraper.get_saved_pids()
        )
        self.assertEqual(Rating(prof="Voinea, Sorin"), rating)

    # NOTE: these are hardcoded values, so subject ot change
    def test_valid_rating(self):
        rating = self.scraper.get_rating(
            "Trepanier, Michele", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Trepanier, Michele",
                avg=2.9,
                takeAgain=48,
                difficulty=3.5,
                nRating=21,
                status="found",
                score=57.3,
            ),
            rating,
        )

    def test_duplicate_rating(self):
        rating: Rating = self.scraper.get_rating(
            "Young, Ryan", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Young, Ryan",
                avg=2.7,
                takeAgain=33,
                difficulty=2.7,
                nRating=6,
                status="found",
                score=53,
            ),
            rating,
        )

        rating: Rating = self.scraper.get_rating(
            "Young, Thomas", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Young, Thomas",
                score=73.1,
                avg=3.8,
                takeAgain=60,
                difficulty=2.4,
                nRating=16,
                status="found",
            ),
            rating,
        )

    # NOTE: belongs to Concordia
    def test_Klochko_Yuliya(self):
        if "Klochko, Yuliya" not in self.professors:
            return

        rating: Rating = self.scraper.get_rating(
            "Klochko, Yuliya", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(prof="Klochko, Yuliya"),
            rating,
        )

    # NOTE: manually check foundn't
    # NOTE: fall2025 june 3 schedule pdf checked!
    # NOTE: missingPids checked!
    def test_accuracy_of_not_found(self):
        checked = True
        updated = True

        if checked:
            if not updated:
                self.updateSectionWithCheckedPids()
            return

        odd: dict[str, str] = {}

        ratings: dict[str, Rating] = self.files.get_ratings_file_content()

        if os.path.exists(self.files.missingPids):
            with open(self.files.missingPids, "r") as file:
                odd = json.loads(file.read())

        for rating in ratings.values():
            if rating.status == "foundn't":
                odd[rating.prof] = ""

        if len(odd) > 0:
            print(json.dumps(odd, indent=2))

        with open(self.files.missingPids, "w") as file:
            file.write(json.dumps(odd, indent=2))

        self.assertEqual(len(odd), 0)

    def updateSectionWithCheckedPids(self):
        ratings = self.files.get_ratings_file_content()
        pids = {
            k: v
            for k, v in self.files.get_missing_pids_file_content().items()
            if v != ""
        }
        new_pids = self.files.get_pids_file_content()
        self.scraper.scrape_ratings(list(pids.keys()), ratings, pids, new_pids)

        self.assertEqual(ratings["Walker, Tara Leigh"].status, "found")

        with open(self.files.ratings, "w") as file:
            file.write(
                json.dumps({k: v.model_dump() for k, v in ratings.items()}, indent=2)
            )

        with open(self.files.pids, "w") as file:
            file.write(json.dumps(new_pids, indent=2))

    def test_special_cases(self):
        rating: Rating = self.scraper.get_rating(
            "Lo Vasco, Frank", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Lo Vasco, Frank",
                avg=3.3,
                takeAgain=51,
                difficulty=4.1,
                nRating=53,
                status="found",
                score=65.4,
            ),
            rating,
        )


if __name__ == "__main__":
    unittest.main()
