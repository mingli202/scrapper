import os


class Files:
    def __init__(self) -> None:
        semester = "winter"
        curPath = os.path.dirname(__file__)
        curPath = curPath[0:-2]
        semesterDir = curPath + semester + "/" + semester

        self.pdfName = curPath + "Schedule of Classes Dec 15.txt"
        self.rawFile = semesterDir + "-raw.json"
        self.classesFile = semesterDir + "-classes.json"
        self.outFile = semesterDir + "-out.json"
        self.organized = semesterDir + "-organized.json"
        self.professors = semesterDir + "-professors.json"
        self.ratings = semesterDir + "-ratings.json"
        self.pids = semesterDir + "-pids.json"
