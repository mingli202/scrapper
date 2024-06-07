import json
from files import Files

semesterFiles = Files("winter")
ratings = semesterFiles.ratings

def main():
    p = set()

    with open(ratings, "r") as file:
        arr = json.loads(file.read())

    for rating in arr:
        # verify if its actually n/a
        # if rating["avg"] == "N/A":
        #     print(rating["prof"])

        # verify if its actually 0
        # if rating["avg"] == 0:
        #     print(rating["prof"])

        # verify if has rating but not found
        # if rating["status"] == "foundn't" and (rating['score'] != 0):
        #     print(rating["prof"])

        lastName = rating["prof"].split(",")[0]
        if lastName in p:
            print(lastName)

        p.add(lastName)
        

     
if __name__ == "__main__":
    main()