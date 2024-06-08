from .files import Files


def main():
    files = Files()
    scraper = Scraper(files)

    scraper.run()


if __name__ == "__main__":
    main()
