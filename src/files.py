import os


class Files:
    def __init__(self) -> None:
        semester = "fall"
        curPath = os.path.dirname(__file__)
        curPath = "/".join(curPath.split("/")[:-1]) + "/"
        semesterDir = curPath + semester + "/" + semester

        self.pdfName = curPath + "SCHEDULE_OF_CLASSES_FALL_2025_June_3.txt"
        self.rawFile = semesterDir + "-raw.json"
        self.classesFile = semesterDir + "-classes.json"
        self.outFile = semesterDir + "-out.json"
        self.organized = semesterDir + "-organized.json"
        self.professors = semesterDir + "-professors.json"
        self.ratings = semesterDir + "-ratings.json"
        self.pids = semesterDir + "-pids.json"
