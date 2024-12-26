from files import Files
from pdf_parser.parser import Parser
from web_scraper.scraper import Scraper


def main():
    files = Files()
    scraper = Parser(files)
    ratings = Scraper(files)

    scraper.run()
    ratings.run()


if __name__ == "__main__":
    main()
