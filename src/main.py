import util
from files import Files
from parser import Parser
from scraper import Scraper


# TODO: 1. Change filename and semester in files.py
def main():
    files = Files()
    scraper = Parser(files)
    ratings = Scraper(files)

    scraper.run()
    ratings.run()

    util.addRating(files)
    util.addViewData(files)


if __name__ == "__main__":
    main()
