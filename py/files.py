import os


class Files:
    def __init__(self, semester) -> None:
        curPath = os.path.dirname(__file__)
        curPath = curPath[0:-2]
        semesterDir = curPath + semester + "/" + semester

        self.pdfName = curPath + "SCHEDULE_OF_CLASSES_June_6.txt"
        self.rawFile = semesterDir + "-raw.json"
        self.classesFile = semesterDir + "-classes.json"
        self.outFile = semesterDir + "-out.json"
        self.organized = semesterDir + "-organized.json"
        self.professors = semesterDir + "-professors.json"
        self.ratings = semesterDir + "-ratings.json"
