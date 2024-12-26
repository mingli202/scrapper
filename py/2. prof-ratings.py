import json
from bs4 import BeautifulSoup
import requests
from files import Files
import re

semesterFiles = Files()
outFile = semesterFiles.outFile
professorsFile = semesterFiles.professors
ratingsFile = semesterFiles.ratings


def writeProfs():
    with open(outFile, "r") as file:
        arr = json.loads(file.read())

    professors = set()

    for index, i in enumerate(arr):
        print(index)

        try:
            professors.add(
                i["lecture"]["prof"].replace("\u00e9", "e").replace("\u00e8", "e")
            )

            if "prof" in i["lab"]:
                professors.add(
                    i["lab"]["prof"].replace("\u00e9", "e").replace("\u00e8", "e")
                )
        except:
            print(f"error id: {i['count']}")
            exit()

    professors.remove("")

    with open(professorsFile, "w") as file:
        file.write(json.dumps(list(professors)))


ratings = []

# professors = ["Lin, Grace Cheng-Ying"]
# professors = ["Trepanier, Michele"]
# JAC_ID = 12050


def stripAccent(s: str):
    s = s.replace("\u00e9", "e")  # * removes é
    s = s.replace("\u00e8", "e")  # * removes è
    s = s.replace("\u00e2", "a")  # * removes â
    s = s.replace("\u00e7", "c")  # * removes ç
    s = s.replace("\u00e0", "a")  # * removes à
    s = s.replace("\u0000", "")  # * removes null character

    return s


def algo(name: str):
    fName = name.split(",")[0].strip().split(" ")
    lName = name.split(",")[1].strip().split(" ")

    # name = Giroux, Cynthia Elaine (Cindy)
    # fName = ["Cynthia", "Elaine", "(Cindy)"]
    # lName = ["Giroux"]

    allCombinasion = [name]

    # first check will the full name
    # if can't fund it, search for a variant of the name
    # finish with first name and last name alone

    for i in fName:
        for j in lName:
            allCombinasion.append(i + " " + j)

    allCombinasion += [name.split(",")[0], name.split(",")[1]]

    return allCombinasion


# known problems:
# teacher has multiple page
# the first name and last name is off my little
# found raint 0 but still foundn't
def getRating(i: str):
    pArr = algo(i)

    fname = i.split(",")[1]
    lname = i.split(",")[0]
    # pArr = [lname]

    print(pArr)

    score = 0
    avg = 0
    nRating = 0
    takeAgain = 0
    difficulty = 0
    status = "foundn't"

    # try for every combinasion of their names
    while len(pArr) != 0:
        comb = pArr.pop().strip()
        p = "%20".join(comb.replace(",", "").split(" "))

        url = f"https://www.ratemyprofessors.com/search/professors/12050?q={p}"

        r = requests.get(url)

        if r.status_code != 200:
            pArr.append(comb)
            print(r.status_code)
            print(p)
            continue

        try:
            legacyId = re.findall(r'"legacyId":(\d+)', r.text)

            for id in legacyId:
                url = f"https://www.ratemyprofessors.com/ShowRatings.jsp?tid={
                    id}"
                r = requests.get(url)

                soup = BeautifulSoup(r.text, "html.parser")

                isJohnAbbott = False
                for anchor in soup.find_all("a"):
                    if anchor.get("href") == "/school/12050":
                        isJohnAbbott = True

                if not isJohnAbbott:
                    raise

                firstName = stripAccent(
                    soup.find(
                        "div", class_="NameTitle__Name-dowf0z-0 cfjPUG"
                    ).span.text.strip()
                )
                lastName = stripAccent(
                    soup.find(
                        "span", class_="NameTitle__LastNameWrapper-dowf0z-2 glXOHH"
                    ).text.strip()
                )

                if len(legacyId) > 1 and lastName != lname and firstName != fname:
                    continue

                try:
                    avg = float(
                        soup.find(
                            "div", class_="RatingValue__Numerator-qw8sqy-2 liyUjw"
                        ).text
                    )
                finally:
                    pass

                try:
                    nRating = float(
                        soup.find(
                            "div", class_="RatingValue__NumRatings-qw8sqy-0 jMkisx"
                        ).div.a.text.replace("ratings", "")
                    )
                finally:
                    pass

                try:
                    takeAgain = float(
                        soup.find_all(
                            "div", class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"
                        )[0].text.replace("%", "")
                    )
                finally:
                    pass

                try:
                    difficulty = float(
                        soup.find_all(
                            "div", class_="FeedbackItem__FeedbackNumber-uof32n-1 kkESWs"
                        )[1].text
                    )
                finally:
                    pass

                status = "found"

            break

        except:
            # continue to next iteration (variant of the name)
            status = "foundn't"

        # print(status)

    # score only for those that exist on the website
    if avg != 0 and nRating != 0:
        """
        Calculated to take into account the number of raters.
        You add one 5/5 and one 0/5 to the rating to obtain the score.
        If there are more raters, the 0/5 will have a lesser impact.

        e.g.
          Gregory, Muclair has 5/5 rating but only 2 raters. His score is 75.0
          Kazuo Takei, Luiz has 4.6/5 rating with 11 raters. His score is 85.5

        More raters makes the rating stronger and accurate.
        """
        score = round((((avg * nRating) + 5) / (nRating + 2)) * 100 / 5, 1)

    # print(score)

    ratings.append(
        {
            "prof": i,
            "score": score,
            "avg": avg,
            "nRating": nRating,
            "takeAgain": takeAgain,
            "difficulty": difficulty,
            "status": status,
        }
    )


def main():
    # bgTasks = set()
    with open(professorsFile, "r") as file:
        professors = json.loads(file.read())

    for i in professors:
        getRating(i)

    # with ThreadPoolExecutor(1000) as exec:
    #     exec.map(getRating, professors)

    with open(ratingsFile, "w") as file:
        print(ratingsFile)
        file.write(json.dumps(ratings, indent=2))


if __name__ == "__main__":
    # writeProfs()
    main()
