import json
from files import Files

semesterFiles = Files()
ratings = semesterFiles.ratings
professorsFile = semesterFiles.professors


def verifyNA(rating):
    if rating["avg"] == "N/A":
        print("NA:", rating["prof"])


def verifyZero(rating):
    if rating["avg"] == 0 and rating["status"] == "found":
        print("0:", rating["prof"])


def verifyNotFound(rating):
    if rating["status"] == "foundn't" and (rating['score'] != 0):
        print("not found:", rating["prof"])


def verifyDuplicateLastName(rating, p):
    lastName = rating["prof"].split(",")[0]
    if lastName in p:
        print("duplicate:", lastName)

    p.add(lastName)


def verifyAllProfs():
    with open(professorsFile, "r") as file:
        professors = json.loads(file.read())

    with open(ratings, "r") as file:
        arr = json.loads(file.read())

    s = {r["prof"] for r in arr}

    for i in professors:
        if i not in s:
            print("No rating for", i)
            return


def main():
    p = set()

    with open(ratings, "r") as file:
        arr = json.loads(file.read())

    for rating in arr:
        verifyNA(rating)
        verifyZero(rating)
        verifyNotFound(rating)
        verifyDuplicateLastName(rating, p)

    verifyAllProfs()


if __name__ == "__main__":
    main()
