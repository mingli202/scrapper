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

    def test_valid_rating(self):
        rating = self.scraper.get_rating(
            "Trepanier, Michele", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Trepanier, Michele",
                avg=3.1,
                takeAgain=47,
                difficulty=3.5,
                nRating=19,
                status="found",
                score=60.9,
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
                avg=2.8,
                takeAgain=34,
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

    def get_ratings(self) -> list[Rating]:
        with open(self.files.ratings, "r") as file:
            return [Rating(**r) for r in from_json(file.read())]

    # NOTE: manually check foundn't
    # WARN: checked! remove this for next semester, ogay
    def test_accuracy_of_not_found(self):
        return
        odd: list[str] = []
        ratings: list[Rating] = self.get_ratings()

        for rating in ratings:
            if rating.status == "foundn't":
                odd.append(rating.prof)

        if len(odd) > 0:
            print(json.dumps(odd, indent=2))

        self.assertEqual(len(odd), 0)

    def test_special_cases(self):
        rating: Rating = self.scraper.get_rating(
            "Lo Vasco, Frank", self.scraper.get_saved_pids()
        )[0]
        self.assertEqual(
            Rating(
                prof="Lo Vasco, Frank",
                avg=3.3,
                takeAgain=52,
                difficulty=4.1,
                nRating=53,
                status="found",
                score=65.4,
            ),
            rating,
        )


if __name__ == "__main__":
    unittest.main()
