import unittest

from pydantic_core import from_json
from files import Files
from models import Section


class OutFileTest(unittest.TestCase):
    def setUp(self):
        self.files = Files()

    # HACK: refactor default prof to ""

    # def test_no_prof(self):
    #     sections: list[Section] = []
    #     with open(self.files.outFile, "r") as file:
    #         sections = [Section(**s) for s in from_json(file.read())]
    #
    #     for section in sections:
    #         self.assertIsNotNone(
    #             section.lecture.get("prof"), f"section {section.count}"
    #         )

    # HACK: refactor default title to ""

    # def test_no_title(self):
    #     sections: list[Section] = []
    #     with open(self.files.outFile, "r") as file:
    #         sections = [Section(**s) for s in from_json(file.read())]
    #
    #     for section in sections:
    #         self.assertIsNotNone(
    #             section.lecture.get("title"), f"section {section.count}"
    #         )
