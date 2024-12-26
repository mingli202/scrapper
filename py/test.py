import unittest

from pydantic_core import from_json
from files import Files

from models import Rating
from web_scraper.scraper import Scraper


class Test(unittest.TestCase):
    def setUp(self) -> None:
        self.files = Files()
        self.scraper = Scraper(self.files)

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
        c = self.scraper.closelness("Grgoy", "Gregory")
        self.assertEqual(c, 5 / 7)

        c = self.scraper.closelness("Greg", "Gregory")
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
        rating: Rating = self.scraper.get_rating("Voinea, Sorin")
        self.assertEqual(Rating(prof="Voinea, Sorin"), rating)

    def test_valid_rating(self):
        rating: Rating = self.scraper.get_rating("Trepanier, Michele")
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
        rating: Rating = self.scraper.get_rating("Young, Ryan")
        self.assertEqual(
            Rating(
                prof="Young, Ryan",
                avg=2.8,
                takeAgain=40,
                difficulty=2.6,
                nRating=5,
                status="found",
                score=54.3,
            ),
            rating,
        )

        rating: Rating = self.scraper.get_rating("Young, Thomas")
        self.assertEqual(
            Rating(
                prof="Young, Thomas",
                score=69.2,
                avg=3.6,
                takeAgain=54,
                difficulty=2.6,
                nRating=14,
                status="found",
            ),
            rating,
        )

    def test_Klochko_Yuliya(self):
        # NOTE: belong to Concordia
        rating: Rating = self.scraper.get_rating("Klochko, Yuliya")
        self.assertEqual(
            Rating(),
            rating,
        )


if __name__ == "__main__":
    unittest.main()
