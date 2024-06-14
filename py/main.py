from files import Files
from pdf_parser.parser import Parser


def main():
    files = Files()
    scraper = Parser(files)

    scraper.run()


if __name__ == "__main__":
    main()
